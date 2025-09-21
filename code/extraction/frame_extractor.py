#!/usr/bin/env python3
"""
Frame Extractor for TikTok Video Content Pipeline

Extracts frames from MP4 files using FFmpeg for OCR processing.
Optimized for M2 Pro with efficient frame sampling strategy.

Author: TikTok Content Analysis Pipeline
Created: January 3, 2025
"""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Optional
import logging

class FrameExtractor:
    """
    Extracts frames from video files using FFmpeg for OCR processing.
    
    Features:
    - Intelligent frame sampling (1 frame per 2-3 seconds)
    - Apple Silicon optimization
    - Error handling and validation
    - Cleanup management
    """
    
    def __init__(self, 
                 output_dir: str = "extracted_content/frames",
                 frame_interval: float = 2.5,
                 image_format: str = "png"):
        """
        Initialize frame extractor.
        
        Args:
            output_dir: Directory to store extracted frames
            frame_interval: Seconds between frame extractions
            image_format: Output image format (png recommended for OCR)
        """
        self.output_dir = Path(output_dir)
        self.frame_interval = frame_interval
        self.image_format = image_format
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def get_video_info(self, video_path: str) -> Optional[dict]:
        """
        Extract video metadata using FFprobe.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video metadata or None if error
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.logger.error(f"FFprobe failed for {video_path}: {result.stderr}")
                return None
                
            metadata = json.loads(result.stdout)
            
            # Extract video stream info
            video_stream = None
            for stream in metadata.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
                    
            if not video_stream:
                self.logger.error(f"No video stream found in {video_path}")
                return None
                
            duration = float(metadata.get('format', {}).get('duration', 0))
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            fps = eval(video_stream.get('r_frame_rate', '0/1'))
            
            return {
                'duration': duration,
                'width': width,
                'height': height,
                'fps': fps,
                'codec': video_stream.get('codec_name', 'unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting video info for {video_path}: {e}")
            return None
    
    def extract_frames(self, video_path: str, video_id: str) -> Tuple[List[str], dict]:
        """
        Extract frames from video at specified intervals.
        
        Args:
            video_path: Path to input video file
            video_id: Unique identifier for the video
            
        Returns:
            Tuple of (list of frame file paths, metadata dict)
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            self.logger.error(f"Video file not found: {video_path}")
            return [], {}
            
        # Get video metadata
        video_info = self.get_video_info(str(video_path))
        if not video_info:
            return [], {}
            
        # Create output directory for this video
        video_frame_dir = self.output_dir / video_id
        video_frame_dir.mkdir(exist_ok=True)
        
        # Calculate frame extraction parameters
        duration = video_info['duration']
        expected_frames = max(1, int(duration / self.frame_interval))
        
        # Construct FFmpeg command for frame extraction
        output_pattern = video_frame_dir / f"frame_%03d.{self.image_format}"
        
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vf', f'fps=1/{self.frame_interval}',  # Extract 1 frame every N seconds
            '-y',  # Overwrite existing files
            '-q:v', '2',  # High quality for OCR
            str(output_pattern)
        ]
        
        try:
            self.logger.info(f"Extracting frames from {video_path.name} (duration: {duration:.1f}s)")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=120  # 2-minute timeout
            )
            
            if result.returncode != 0:
                self.logger.error(f"FFmpeg extraction failed for {video_id}: {result.stderr}")
                return [], video_info
                
            # Find extracted frames
            frame_files = list(video_frame_dir.glob(f"*.{self.image_format}"))
            frame_files.sort()  # Ensure chronological order
            
            # Add frame metadata
            video_info.update({
                'frames_extracted': len(frame_files),
                'frames_expected': expected_frames,
                'frame_interval': self.frame_interval,
                'frame_directory': str(video_frame_dir)
            })
            
            self.logger.info(f"Extracted {len(frame_files)} frames from {video_id}")
            
            return [str(f) for f in frame_files], video_info
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Frame extraction timeout for {video_id}")
            return [], video_info
        except Exception as e:
            self.logger.error(f"Unexpected error extracting frames from {video_id}: {e}")
            return [], video_info
    
    def cleanup_frames(self, video_id: str) -> bool:
        """
        Clean up extracted frames for a video to save disk space.
        
        Args:
            video_id: Video identifier
            
        Returns:
            True if cleanup successful
        """
        try:
            video_frame_dir = self.output_dir / video_id
            if video_frame_dir.exists():
                import shutil
                shutil.rmtree(video_frame_dir)
                self.logger.debug(f"Cleaned up frames for {video_id}")
                return True
        except Exception as e:
            self.logger.error(f"Error cleaning up frames for {video_id}: {e}")
            
        return False
    
    def get_frame_timestamps(self, frame_files: List[str]) -> List[float]:
        """
        Calculate timestamps for extracted frames based on frame interval.
        
        Args:
            frame_files: List of frame file paths
            
        Returns:
            List of timestamps in seconds
        """
        timestamps = []
        for i, frame_file in enumerate(frame_files):
            timestamp = i * self.frame_interval
            timestamps.append(timestamp)
            
        return timestamps


def main():
    """Test the frame extractor with a sample video."""
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) != 2:
        print("Usage: python frame_extractor.py <video_path>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    video_id = Path(video_path).stem
    
    extractor = FrameExtractor()
    frames, metadata = extractor.extract_frames(video_path, video_id)
    
    print(f"Extracted {len(frames)} frames")
    print(f"Metadata: {json.dumps(metadata, indent=2)}")
    
    if frames:
        print(f"Sample frame: {frames[0]}")
        timestamps = extractor.get_frame_timestamps(frames)
        print(f"Frame timestamps: {timestamps}")


if __name__ == "__main__":
    main()