#!/usr/bin/env python3
"""
Utilities for TikTok Video Content Pipeline

Common utilities for progress tracking, error handling, and system monitoring.

Author: TikTok Content Analysis Pipeline  
Created: January 3, 2025
"""

import os
import json
import time
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class ProcessingProgress:
    """Data class for tracking processing progress."""
    total_videos: int
    completed_videos: int
    failed_videos: int
    start_time: datetime
    current_video: str = ""
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    @property
    def completion_rate(self) -> float:
        """Calculate completion percentage."""
        if self.total_videos == 0:
            return 0.0
        return (self.completed_videos / self.total_videos) * 100
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure percentage."""
        if self.completed_videos + self.failed_videos == 0:
            return 0.0
        return (self.failed_videos / (self.completed_videos + self.failed_videos)) * 100
    
    @property
    def elapsed_time(self) -> timedelta:
        """Calculate elapsed processing time."""
        return datetime.now() - self.start_time
    
    @property
    def estimated_remaining(self) -> Optional[timedelta]:
        """Estimate remaining processing time."""
        if self.completed_videos == 0:
            return None
        
        elapsed = self.elapsed_time
        rate = self.completed_videos / elapsed.total_seconds()
        remaining_videos = self.total_videos - self.completed_videos - self.failed_videos
        
        if rate > 0:
            remaining_seconds = remaining_videos / rate
            return timedelta(seconds=remaining_seconds)
        
        return None


class ProgressTracker:
    """
    Tracks and persists processing progress with resume capability.
    
    Features:
    - JSON-based progress persistence
    - ETA calculation
    - Real-time progress display
    - Error tracking and reporting
    """
    
    def __init__(self, progress_file: str = "extracted_content/progress/progress.json"):
        """
        Initialize progress tracker.
        
        Args:
            progress_file: Path to progress JSON file
        """
        self.progress_file = Path(progress_file)
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Progress state
        self.progress: Optional[ProcessingProgress] = None
        
    def start_processing(self, total_videos: int, resume: bool = True) -> ProcessingProgress:
        """
        Start or resume processing session.
        
        Args:
            total_videos: Total number of videos to process
            resume: Whether to resume from existing progress
            
        Returns:
            ProcessingProgress object
        """
        if resume and self.progress_file.exists():
            self.progress = self.load_progress()
            if self.progress and self.progress.total_videos == total_videos:
                self.logger.info(f"Resuming processing from {self.progress.completed_videos}/{total_videos}")
                return self.progress
        
        # Start new processing session
        self.progress = ProcessingProgress(
            total_videos=total_videos,
            completed_videos=0,
            failed_videos=0,
            start_time=datetime.now()
        )
        
        self.save_progress()
        self.logger.info(f"Starting new processing session: {total_videos} videos")
        return self.progress
    
    def update_progress(self, 
                       current_video: str = "",
                       completed: bool = False,
                       failed: bool = False,
                       error_message: str = "") -> None:
        """
        Update processing progress.
        
        Args:
            current_video: Currently processing video ID
            completed: Whether current video completed successfully
            failed: Whether current video failed
            error_message: Error message if failed
        """
        if not self.progress:
            raise ValueError("Progress tracking not started")
        
        self.progress.current_video = current_video
        
        if completed:
            self.progress.completed_videos += 1
        
        if failed:
            self.progress.failed_videos += 1
            if error_message:
                self.progress.errors.append(f"{current_video}: {error_message}")
        
        # Save progress periodically
        if (self.progress.completed_videos + self.progress.failed_videos) % 10 == 0:
            self.save_progress()
    
    def save_progress(self) -> bool:
        """
        Save current progress to JSON file.
        
        Returns:
            True if successful
        """
        if not self.progress:
            return False
        
        try:
            progress_data = {
                'total_videos': self.progress.total_videos,
                'completed_videos': self.progress.completed_videos,
                'failed_videos': self.progress.failed_videos,
                'start_time': self.progress.start_time.isoformat(),
                'current_video': self.progress.current_video,
                'errors': self.progress.errors[-50:]  # Keep last 50 errors
            }
            
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving progress: {e}")
            return False
    
    def load_progress(self) -> Optional[ProcessingProgress]:
        """
        Load progress from JSON file.
        
        Returns:
            ProcessingProgress object or None if failed
        """
        try:
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
            
            progress = ProcessingProgress(
                total_videos=data['total_videos'],
                completed_videos=data['completed_videos'],
                failed_videos=data['failed_videos'],
                start_time=datetime.fromisoformat(data['start_time']),
                current_video=data.get('current_video', ''),
                errors=data.get('errors', [])
            )
            
            return progress
            
        except Exception as e:
            self.logger.error(f"Error loading progress: {e}")
            return None
    
    def get_processed_videos(self) -> set:
        """
        Get set of video IDs that have been processed (completed or failed).
        
        Returns:
            Set of processed video IDs
        """
        # This would typically read from the main CSV file
        # For now, return empty set - implement based on CSV reader
        return set()
    
    def print_progress(self, force: bool = False) -> None:
        """
        Print current progress to console.
        
        Args:
            force: Force printing even if not at interval
        """
        if not self.progress:
            return
        
        # Print every 10 videos or if forced
        total_processed = self.progress.completed_videos + self.progress.failed_videos
        if not force and total_processed % 10 != 0:
            return
        
        completion = self.progress.completion_rate
        elapsed = self.progress.elapsed_time
        remaining = self.progress.estimated_remaining
        
        print(f"\n📊 Processing Progress:")
        print(f"   Completed: {self.progress.completed_videos}/{self.progress.total_videos} ({completion:.1f}%)")
        print(f"   Failed: {self.progress.failed_videos} ({self.progress.failure_rate:.1f}%)")
        print(f"   Current: {self.progress.current_video}")
        print(f"   Elapsed: {str(elapsed).split('.')[0]}")
        
        if remaining:
            print(f"   Remaining: {str(remaining).split('.')[0]}")
        
        # System stats
        system_stats = get_system_stats()
        print(f"   CPU: {system_stats['cpu_percent']}% | RAM: {system_stats['memory_percent']}% | Temp: {system_stats['temperature']}°C")


class SystemMonitor:
    """
    Monitors system resources during processing.
    
    Features:
    - CPU and memory usage tracking
    - Temperature monitoring (Apple Silicon)
    - Disk space monitoring
    - Performance alerts
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        memory = psutil.virtual_memory()
        return {
            'total_gb': memory.total / (1024**3),
            'used_gb': memory.used / (1024**3),
            'available_gb': memory.available / (1024**3),
            'percent': memory.percent
        }
    
    def get_disk_usage(self, path: str = ".") -> Dict[str, float]:
        """Get disk usage for specified path."""
        disk = psutil.disk_usage(path)
        return {
            'total_gb': disk.total / (1024**3),
            'used_gb': disk.used / (1024**3),
            'free_gb': disk.free / (1024**3),
            'percent': (disk.used / disk.total) * 100
        }
    
    def get_temperature(self) -> Optional[float]:
        """Get CPU temperature (Apple Silicon specific)."""
        try:
            # This is a simplified approach - actual implementation may vary
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        return entries[0].current
        except:
            pass
        
        return None
    
    def check_resources(self) -> Dict[str, Any]:
        """
        Check all system resources and return status.
        
        Returns:
            Dictionary with resource status and warnings
        """
        cpu_usage = self.get_cpu_usage()
        memory = self.get_memory_usage()
        disk = self.get_disk_usage()
        temp = self.get_temperature()
        
        warnings = []
        
        # Check for resource constraints
        if cpu_usage > 90:
            warnings.append("High CPU usage")
        
        if memory['percent'] > 85:
            warnings.append("High memory usage")
        
        if disk['percent'] > 90:
            warnings.append("Low disk space")
        
        if temp and temp > 80:
            warnings.append("High CPU temperature")
        
        return {
            'cpu_percent': cpu_usage,
            'memory_percent': memory['percent'],
            'memory_available_gb': memory['available_gb'],
            'disk_free_gb': disk['free_gb'],
            'temperature': temp,
            'warnings': warnings,
            'status': 'warning' if warnings else 'ok'
        }


def get_system_stats() -> Dict[str, Any]:
    """
    Get quick system statistics.
    
    Returns:
        Dictionary with basic system stats
    """
    monitor = SystemMonitor()
    return monitor.check_resources()


def setup_logging(log_file: str = "logs/video_processing.log", level: int = logging.INFO) -> None:
    """
    Setup logging configuration for the pipeline.
    
    Args:
        log_file: Path to log file
        level: Logging level
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def create_batch_list(video_files: List[str], batch_size: int = 100) -> List[List[str]]:
    """
    Split video files into batches for processing.
    
    Args:
        video_files: List of video file paths
        batch_size: Number of videos per batch
        
    Returns:
        List of batches (each batch is a list of video paths)
    """
    batches = []
    for i in range(0, len(video_files), batch_size):
        batch = video_files[i:i + batch_size]
        batches.append(batch)
    
    return batches


def cleanup_temp_files(temp_dir: str, max_age_hours: int = 24) -> None:
    """
    Clean up temporary files older than specified age.
    
    Args:
        temp_dir: Directory containing temporary files
        max_age_hours: Maximum age in hours for temp files
    """
    try:
        temp_path = Path(temp_dir)
        if not temp_path.exists():
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for file_path in temp_path.rglob('*'):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
    
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error cleaning temp files: {e}")


def validate_video_file(video_path: str) -> bool:
    """
    Validate that a video file exists and is accessible.
    
    Args:
        video_path: Path to video file
        
    Returns:
        True if valid
    """
    try:
        path = Path(video_path)
        if not path.exists():
            return False
        
        if not path.is_file():
            return False
        
        if path.stat().st_size < 1000:  # Less than 1KB is suspicious
            return False
        
        return True
        
    except Exception:
        return False


def estimate_processing_time(total_videos: int, avg_time_per_video: float = 75.0) -> Dict[str, str]:
    """
    Estimate total processing time.
    
    Args:
        total_videos: Number of videos to process
        avg_time_per_video: Average seconds per video
        
    Returns:
        Dictionary with time estimates
    """
    total_seconds = total_videos * avg_time_per_video
    
    # Sequential processing
    sequential_time = timedelta(seconds=total_seconds)
    
    # Concurrent processing (assume 8 workers)
    concurrent_time = timedelta(seconds=total_seconds / 8)
    
    return {
        'sequential': str(sequential_time).split('.')[0],
        'concurrent_8_workers': str(concurrent_time).split('.')[0],
        'total_videos': total_videos,
        'avg_seconds_per_video': avg_time_per_video
    }


def main():
    """Test utilities."""
    # Test progress tracking
    tracker = ProgressTracker("test_progress.json")
    progress = tracker.start_processing(100)
    
    # Simulate some processing
    for i in range(5):
        tracker.update_progress(f"video_{i}", completed=True)
    
    tracker.update_progress("video_5", failed=True, error_message="Test error")
    tracker.print_progress(force=True)
    
    # Test system monitoring
    stats = get_system_stats()
    print(f"\nSystem Stats: {stats}")
    
    # Test time estimation
    estimates = estimate_processing_time(4445)
    print(f"\nTime Estimates: {estimates}")


if __name__ == "__main__":
    main()