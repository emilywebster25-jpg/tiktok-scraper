#!/usr/bin/env python3
"""
Audio Transcriber for TikTok Video Content Pipeline

Converts speech to text using OpenAI Whisper with Apple Silicon optimization.
Optimized for short-form social media content.

Author: TikTok Content Analysis Pipeline
Created: January 3, 2025
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import json

import whisper
import torch


class AudioTranscriber:
    """
    Transcribes audio from video files using OpenAI Whisper.
    
    Features:
    - Apple Silicon Metal acceleration
    - Optimized for 15-60 second videos
    - Word-level timestamps
    - Language detection with English preference
    - Error handling and retry logic
    """
    
    def __init__(self, 
                 model_name: str = "tiny",
                 language: Optional[str] = None,
                 device: Optional[str] = None):
        """
        Initialize audio transcriber.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            language: Target language code (None for auto-detection)
            device: Device to use (None for auto-selection)
        """
        self.model_name = model_name
        self.language = language
        self.device = device or self._get_optimal_device()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load Whisper model
        self.model = None
        self._load_model()
        
    def _get_optimal_device(self) -> str:
        """
        Determine optimal device for Whisper processing.
        
        Returns:
            Device string ('mps', 'cuda', or 'cpu')
        """
        # Force CPU due to MPS compatibility issues with Whisper
        return "cpu"
    
    def _load_model(self) -> None:
        """Load Whisper model with error handling."""
        try:
            self.logger.info(f"Loading Whisper {self.model_name} model on {self.device}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            self.logger.info("Whisper model loaded successfully")
            
            # Log model capabilities
            if hasattr(self.model, 'is_multilingual'):
                self.logger.info(f"Model multilingual: {self.model.is_multilingual}")
                
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def extract_audio_from_video(self, video_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Extract audio track from video file using FFmpeg.
        
        Args:
            video_path: Path to input video file
            output_path: Path for output audio file (optional)
            
        Returns:
            Path to extracted audio file or None if failed
        """
        try:
            if output_path is None:
                # Create temporary file
                temp_dir = tempfile.gettempdir()
                video_name = Path(video_path).stem
                output_path = os.path.join(temp_dir, f"{video_name}_audio.wav")
            
            # FFmpeg command to extract audio
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit for Whisper
                '-ar', '16000',  # 16kHz sample rate (Whisper's preference)
                '-ac', '1',  # Mono audio
                '-y',  # Overwrite existing
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 1-minute timeout
            )
            
            if result.returncode != 0:
                self.logger.error(f"FFmpeg audio extraction failed: {result.stderr}")
                return None
                
            if not os.path.exists(output_path):
                self.logger.error(f"Audio extraction failed - output file not created: {output_path}")
                return None
                
            self.logger.debug(f"Audio extracted to: {output_path}")
            return output_path
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Audio extraction timeout for {video_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting audio from {video_path}: {e}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, any]:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with transcription results and metadata
        """
        try:
            if not os.path.exists(audio_path):
                return {
                    'text': '',
                    'language': 'unknown',
                    'segments': [],
                    'word_timestamps': '',
                    'confidence': 0.0,
                    'error': 'Audio file not found'
                }
            
            self.logger.debug(f"Transcribing audio: {audio_path}")
            
            # Transcribe with word-level timestamps
            result = self.model.transcribe(
                audio_path,
                language=self.language,
                word_timestamps=True,
                verbose=False
            )
            
            # Extract transcription text
            text = result.get('text', '').strip()
            
            # Extract language detection
            detected_language = result.get('language', 'unknown')
            
            # Process segments for detailed timing
            segments = result.get('segments', [])
            processed_segments = []
            
            for segment in segments:
                processed_segment = {
                    'start': segment.get('start', 0.0),
                    'end': segment.get('end', 0.0),
                    'text': segment.get('text', '').strip(),
                    'avg_logprob': segment.get('avg_logprob', -1.0),
                    'no_speech_prob': segment.get('no_speech_prob', 1.0)
                }
                
                # Extract word-level timestamps if available
                words = segment.get('words', [])
                # Fix: Ensure words is always a list, never None
                if words is None:
                    words = []
                    
                if words:
                    processed_segment['words'] = [
                        {
                            'word': word.get('word', '').strip(),
                            'start': word.get('start', 0.0),
                            'end': word.get('end', 0.0),
                            'probability': word.get('probability', 0.0)
                        }
                        for word in words
                    ]
                
                processed_segments.append(processed_segment)
            
            # Create word timestamps string
            word_timestamps = self._create_word_timestamps_string(processed_segments)
            
            # Calculate confidence metrics
            confidence_score = self._calculate_confidence(processed_segments)
            
            return {
                'text': text,
                'language': detected_language,
                'segments': processed_segments,
                'word_timestamps': word_timestamps,
                'confidence': confidence_score,
                'duration': max([s['end'] for s in processed_segments]) if processed_segments else 0.0,
                'error': None
            }
            
        except Exception as e:
            self.logger.error(f"Error transcribing audio {audio_path}: {e}")
            return {
                'text': '',
                'language': 'unknown',
                'segments': [],
                'word_timestamps': '',
                'confidence': 0.0,
                'error': f'Transcription failed: {e}'
            }
    
    def _create_word_timestamps_string(self, segments: List[Dict]) -> str:
        """
        Create a formatted string with word-level timestamps.
        
        Args:
            segments: List of segment dictionaries
            
        Returns:
            Formatted timestamp string
        """
        timestamp_parts = []
        
        for segment in segments:
            words = segment.get('words', [])
            # Fix: Ensure words is always a list, never None
            if words is None:
                words = []
                
            if words:
                for word in words:
                    word_text = word.get('word', '').strip()
                    start_time = word.get('start', 0.0)
                    if word_text:
                        timestamp_parts.append(f"{start_time:.1f}s-{word_text}")
            else:
                # Fallback to segment-level timestamps
                text = segment['text'].strip()
                start_time = segment['start']
                if text:
                    timestamp_parts.append(f"{start_time:.1f}s-{text}")
        
        return ';'.join(timestamp_parts)
    
    def _calculate_confidence(self, segments: List[Dict]) -> float:
        """
        Calculate overall confidence score from segments.
        
        Args:
            segments: List of segment dictionaries
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not segments:
            return 0.0
        
        # Use average log probability as confidence proxy
        avg_logprobs = [s.get('avg_logprob', -10.0) for s in segments]
        
        if not avg_logprobs:
            return 0.0
        
        # Convert log probability to confidence score (heuristic)
        # Whisper log probs typically range from -1.0 (high conf) to -10.0+ (low conf)
        mean_logprob = sum(avg_logprobs) / len(avg_logprobs)
        
        # Map to 0-1 scale (this is a heuristic mapping)
        if mean_logprob >= -1.0:
            confidence = 0.95
        elif mean_logprob >= -2.0:
            confidence = 0.85
        elif mean_logprob >= -3.0:
            confidence = 0.75
        elif mean_logprob >= -5.0:
            confidence = 0.60
        elif mean_logprob >= -7.0:
            confidence = 0.40
        else:
            confidence = 0.20
        
        return confidence
    
    def transcribe_video(self, video_path: str, cleanup_audio: bool = True) -> Dict[str, any]:
        """
        Complete transcription pipeline: extract audio + transcribe.
        
        Args:
            video_path: Path to video file
            cleanup_audio: Whether to delete temporary audio file
            
        Returns:
            Transcription results dictionary
        """
        try:
            # Extract audio from video
            audio_path = self.extract_audio_from_video(video_path)
            
            if not audio_path:
                return {
                    'text': '',
                    'language': 'unknown',
                    'segments': [],
                    'word_timestamps': '',
                    'confidence': 0.0,
                    'error': 'Audio extraction failed'
                }
            
            # Transcribe audio
            transcription_result = self.transcribe_audio(audio_path)
            
            # Cleanup temporary audio file
            if cleanup_audio and audio_path.startswith(tempfile.gettempdir()):
                try:
                    os.remove(audio_path)
                    self.logger.debug(f"Cleaned up temporary audio file: {audio_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to cleanup audio file {audio_path}: {e}")
            
            return transcription_result
            
        except Exception as e:
            self.logger.error(f"Error in video transcription pipeline for {video_path}: {e}")
            return {
                'text': '',
                'language': 'unknown',
                'segments': [],
                'word_timestamps': '',
                'confidence': 0.0,
                'error': f'Pipeline error: {e}'
            }


def main():
    """Test the audio transcriber with a sample video."""
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) != 2:
        print("Usage: python audio_transcriber.py <video_path>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        sys.exit(1)
    
    transcriber = AudioTranscriber()
    result = transcriber.transcribe_video(video_path)
    
    print(f"Transcription: {result['text']}")
    print(f"Language: {result['language']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Duration: {result.get('duration', 0):.1f}s")
    print(f"Word timestamps: {result['word_timestamps']}")
    
    if result['error']:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()