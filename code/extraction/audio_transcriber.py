#!/usr/bin/env python3
"""
Fixed Audio Transcriber with better error handling
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

import whisper
import numpy as np


class AudioTranscriber:
    """Fixed version with robust error handling"""
    
    def __init__(self, 
                 model_name: str = "tiny",
                 language: Optional[str] = None,
                 device: Optional[str] = None):
        self.model_name = model_name
        self.language = language
        self.device = device or "cpu"
        self.logger = logging.getLogger(__name__)
        self.model = None
        self._load_model()
        
    def _load_model(self) -> None:
        """Load Whisper model with error handling."""
        try:
            self.logger.info(f"Loading Whisper {self.model_name} model on {self.device}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            self.logger.info("Whisper model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def extract_audio_from_video(self, video_path: str) -> Optional[str]:
        """Extract audio from video file."""
        import subprocess
        
        try:
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio:
                audio_path = tmp_audio.name
            
            # Extract audio using ffmpeg
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"FFmpeg audio extraction failed: {result.stderr}")
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                return None
                
            # Verify audio file is not empty
            if os.path.getsize(audio_path) < 1000:  # Less than 1KB
                self.logger.warning(f"Extracted audio file is too small: {os.path.getsize(audio_path)} bytes")
                os.remove(audio_path)
                return None
                
            return audio_path
            
        except Exception as e:
            self.logger.error(f"Error extracting audio from {video_path}: {e}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio with comprehensive error handling."""
        try:
            if not os.path.exists(audio_path):
                return self._error_result('Audio file not found')
            
            # Try transcription with basic options first
            try:
                # Simple transcription without word timestamps
                result = self.model.transcribe(
                    audio_path,
                    language=self.language,
                    word_timestamps=False,  # Disable to avoid issues
                    verbose=False,
                    fp16=False  # Force FP32
                )
                
                # Extract basic info
                text = result.get('text', '').strip()
                language = result.get('language', 'unknown')
                
                # Process segments safely
                segments = result.get('segments', [])
                processed_segments = []
                
                for segment in segments:
                    if segment is None:
                        continue
                        
                    processed_segment = {
                        'start': float(segment.get('start', 0.0)),
                        'end': float(segment.get('end', 0.0)),
                        'text': str(segment.get('text', '')).strip()
                    }
                    processed_segments.append(processed_segment)
                
                # Create simple timestamps
                timestamps = []
                for seg in processed_segments:
                    if seg['text']:
                        timestamps.append(f"{seg['start']:.1f}s-{seg['text']}")
                
                return {
                    'text': text,
                    'language': language,
                    'segments': processed_segments,
                    'word_timestamps': ';'.join(timestamps),
                    'confidence': 0.6 if text else 0.0,  # Simple confidence
                    'duration': max([s['end'] for s in processed_segments]) if processed_segments else 0.0,
                    'error': None,
                    'success': True
                }
                
            except Exception as e:
                # If basic transcription fails, return error
                self.logger.error(f"Transcription failed: {type(e).__name__}: {e}")
                return self._error_result(f'Transcription failed: {type(e).__name__}: {str(e)[:100]}')
                
        except Exception as e:
            self.logger.error(f"Unexpected error in transcribe_audio: {e}")
            return self._error_result(f'Unexpected error: {type(e).__name__}')
    
    def _error_result(self, error_msg: str) -> Dict[str, Any]:
        """Return error result dictionary."""
        return {
            'text': '',
            'language': 'unknown',
            'segments': [],
            'word_timestamps': '',
            'confidence': 0.0,
            'duration': 0.0,
            'error': error_msg,
            'success': False
        }
    
    def transcribe_video(self, video_path: str, cleanup_audio: bool = True) -> Dict[str, Any]:
        """Complete transcription pipeline."""
        try:
            # Extract audio
            audio_path = self.extract_audio_from_video(video_path)
            
            if not audio_path:
                return self._error_result('Audio extraction failed')
            
            # Transcribe
            result = self.transcribe_audio(audio_path)
            
            # Cleanup
            if cleanup_audio and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except:
                    pass
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in transcribe_video: {e}")
            return self._error_result(f'Pipeline error: {type(e).__name__}')