#!/usr/bin/env python3
"""
Pipeline Controller for TikTok Video Content Extraction

Main orchestrator for the video content extraction pipeline.
Coordinates frame extraction, OCR, transcription, and data output.

Author: TikTok Content Analysis Pipeline
Created: January 3, 2025
"""

import os
import sys
import glob
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import traceback

# Import pipeline components
from frame_extractor import FrameExtractor
from ocr_processor import OCRProcessor
from audio_transcriber import AudioTranscriber
from data_merger import DataMerger
from utils import (
    ProgressTracker, 
    setup_logging, 
    get_system_stats, 
    validate_video_file,
    estimate_processing_time,
    create_batch_list,
    cleanup_temp_files
)


class VideoPipelineController:
    """
    Main controller for the video content extraction pipeline.
    
    Features:
    - Concurrent processing with configurable workers
    - Resume capability for interrupted sessions
    - Comprehensive error handling and logging
    - Real-time progress monitoring
    - System resource monitoring
    """
    
    def __init__(self, 
                 videos_dir: str = "videos",
                 output_dir: str = "extracted_content",
                 num_workers: int = 1,
                 batch_size: int = 100):
        """
        Initialize pipeline controller.
        
        Args:
            videos_dir: Directory containing MP4 files
            output_dir: Directory for output files
            num_workers: Number of concurrent workers
            batch_size: Videos per batch for progress tracking
        """
        self.videos_dir = Path(videos_dir)
        self.output_dir = Path(output_dir)
        self.num_workers = num_workers
        self.batch_size = batch_size
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize pipeline components
        self.frame_extractor = FrameExtractor(
            output_dir=str(self.output_dir / "frames")
        )
        
        self.ocr_processor = OCRProcessor(
            confidence_threshold=30,
            similarity_threshold=0.8
        )
        
        self.audio_transcriber = AudioTranscriber(
            model_name="tiny"
        )
        
        self.data_merger = DataMerger(
            output_dir=str(self.output_dir)
        )
        
        self.progress_tracker = ProgressTracker(
            progress_file=str(self.output_dir / "progress" / "progress.json")
        )
        
        # Main output file
        self.output_csv = "video_content_analysis.csv"
        
    def find_video_files(self) -> List[str]:
        """
        Find all MP4 files in the videos directory.
        
        Returns:
            List of video file paths
        """
        video_pattern = str(self.videos_dir / "*.mp4")
        video_files = glob.glob(video_pattern)
        
        # Validate files
        valid_files = []
        for video_file in video_files:
            if validate_video_file(video_file):
                valid_files.append(video_file)
            else:
                self.logger.warning(f"Invalid video file: {video_file}")
        
        self.logger.info(f"Found {len(valid_files)} valid video files")
        return sorted(valid_files)
    
    def extract_video_id(self, video_path: str) -> str:
        """
        Extract video ID from filename.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Video ID string
        """
        filename = Path(video_path).stem
        
        # TikTok video IDs are typically at the end of the filename
        # Format: search_term_creator_videoId.mp4
        parts = filename.split('_')
        if len(parts) >= 2:
            # Last part should be the video ID
            video_id = parts[-1]
            # Validate it looks like a TikTok ID (numeric, ~19 digits)
            if video_id.isdigit() and len(video_id) > 15:
                return video_id
        
        # Fallback to full filename
        return filename
    
    def process_single_video(self, video_path: str) -> Dict[str, any]:
        """
        Process a single video through the complete pipeline.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with processing results
        """
        video_id = self.extract_video_id(video_path)
        filename = Path(video_path).name
        
        try:
            self.logger.info(f"Processing video: {video_id}")
            
            # Step 1: Extract frames
            self.logger.debug(f"Extracting frames for {video_id}")
            frames, video_metadata = self.frame_extractor.extract_frames(video_path, video_id)
            
            if not frames:
                return {
                    'video_id': video_id,
                    'filename': filename,
                    'video_metadata': video_metadata,
                    'ocr_results': {'error': 'Frame extraction failed'},
                    'transcription_results': {'error': 'No frames to process'},
                    'processing_time': 0
                }
            
            # Step 2: Process frames with OCR
            self.logger.debug(f"Running OCR on {len(frames)} frames for {video_id}")
            timestamps = self.frame_extractor.get_frame_timestamps(frames)
            ocr_results = self.ocr_processor.process_frame_sequence(frames, timestamps)
            
            # Step 3: Transcribe audio
            self.logger.debug(f"Transcribing audio for {video_id}")
            transcription_results = self.audio_transcriber.transcribe_video(video_path)
            
            # Step 4: Cleanup temporary frames
            self.frame_extractor.cleanup_frames(video_id)
            
            return {
                'video_id': video_id,
                'filename': filename,
                'video_metadata': video_metadata,
                'ocr_results': ocr_results,
                'transcription_results': transcription_results,
                'processing_time': 0  # Could add timing here
            }
            
        except Exception as e:
            self.logger.error(f"Error processing video {video_id}: {e}")
            self.logger.debug(traceback.format_exc())
            
            # Cleanup on error
            try:
                self.frame_extractor.cleanup_frames(video_id)
            except:
                pass
            
            return {
                'video_id': video_id,
                'filename': filename,
                'video_metadata': {},
                'ocr_results': {'error': f'Processing failed: {e}'},
                'transcription_results': {'error': f'Processing failed: {e}'},
                'processing_time': 0
            }
    
    def process_batch(self, video_files: List[str]) -> List[Dict[str, any]]:
        """
        Process a batch of videos concurrently.
        
        Args:
            video_files: List of video file paths
            
        Returns:
            List of processing results
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # Submit all videos in batch
            future_to_video = {
                executor.submit(self.process_single_video, video_file): video_file
                for video_file in video_files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_video):
                video_file = future_to_video[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Update progress
                    video_id = result['video_id']
                    has_error = (result['ocr_results'].get('error') and 
                               result['transcription_results'].get('error'))
                    
                    if has_error:
                        error_msg = result['ocr_results'].get('error', 'Unknown error')
                        self.progress_tracker.update_progress(
                            current_video=video_id,
                            failed=True,
                            error_message=error_msg
                        )
                    else:
                        self.progress_tracker.update_progress(
                            current_video=video_id,
                            completed=True
                        )
                    
                    # Print progress periodically
                    self.progress_tracker.print_progress()
                    
                except Exception as e:
                    self.logger.error(f"Error in future for {video_file}: {e}")
                    results.append({
                        'video_id': self.extract_video_id(video_file),
                        'filename': Path(video_file).name,
                        'video_metadata': {},
                        'ocr_results': {'error': f'Future error: {e}'},
                        'transcription_results': {'error': f'Future error: {e}'},
                        'processing_time': 0
                    })
        
        return results
    
    def save_batch_results(self, results: List[Dict[str, any]]) -> bool:
        """
        Save batch results to CSV and create summary.
        
        Args:
            results: List of processing results
            
        Returns:
            True if successful
        """
        try:
            # Convert results to records and save to CSV
            for result in results:
                record = self.data_merger.create_video_record(
                    video_id=result['video_id'],
                    filename=result['filename'],
                    video_metadata=result['video_metadata'],
                    ocr_results=result['ocr_results'],
                    transcription_results=result['transcription_results']
                )
                
                # Validate record
                is_valid, errors = self.data_merger.validate_record(record)
                if not is_valid:
                    self.logger.warning(f"Invalid record for {result['video_id']}: {errors}")
                
                # Save to CSV
                self.data_merger.append_to_csv(record, self.output_csv)
            
            # Create and save batch summary
            records = [
                self.data_merger.create_video_record(
                    video_id=r['video_id'],
                    filename=r['filename'],
                    video_metadata=r['video_metadata'],
                    ocr_results=r['ocr_results'],
                    transcription_results=r['transcription_results']
                )
                for r in results
            ]
            
            summary = self.data_merger.create_batch_summary(records)
            self.data_merger.save_batch_summary(summary)
            
            self.logger.info(f"Saved {len(results)} results to {self.output_csv}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving batch results: {e}")
            return False
    
    def run_pipeline(self, resume: bool = True, max_videos: Optional[int] = None) -> bool:
        """
        Run the complete video processing pipeline.
        
        Args:
            resume: Whether to resume from previous progress
            max_videos: Maximum number of videos to process (for testing)
            
        Returns:
            True if successful
        """
        try:
            self.logger.info("Starting TikTok Video Content Extraction Pipeline")
            
            # Find video files
            video_files = self.find_video_files()
            
            if not video_files:
                self.logger.error("No video files found")
                return False
            
            # Limit for testing
            if max_videos:
                video_files = video_files[:max_videos]
                self.logger.info(f"Limited to {max_videos} videos for testing")
            
            # Check for resume
            processed_ids = set()
            if resume:
                processed_ids = self.data_merger.get_processed_video_ids(self.output_csv)
                self.logger.info(f"Found {len(processed_ids)} previously processed videos")
            
            # Filter out already processed videos
            remaining_files = []
            for video_file in video_files:
                video_id = self.extract_video_id(video_file)
                if video_id not in processed_ids:
                    remaining_files.append(video_file)
            
            if not remaining_files:
                self.logger.info("All videos already processed")
                return True
            
            self.logger.info(f"Processing {len(remaining_files)} remaining videos")
            
            # Start progress tracking
            self.progress_tracker.start_processing(len(remaining_files), resume=resume)
            
            # Print initial estimates
            estimates = estimate_processing_time(len(remaining_files))
            self.logger.info(f"Estimated processing time: {estimates['concurrent_8_workers']}")
            
            # Process in batches
            batches = create_batch_list(remaining_files, self.batch_size)
            
            for batch_num, batch in enumerate(batches, 1):
                self.logger.info(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} videos)")
                
                # Check system resources
                stats = get_system_stats()
                if stats['warnings']:
                    self.logger.warning(f"System warnings: {stats['warnings']}")
                
                # Process batch
                results = self.process_batch(batch)
                
                # Save results
                if not self.save_batch_results(results):
                    self.logger.error(f"Failed to save batch {batch_num} results")
                    return False
                
                # Cleanup temp files periodically
                if batch_num % 5 == 0:
                    cleanup_temp_files(str(self.output_dir / "frames"))
            
            # Final progress update
            self.progress_tracker.save_progress()
            self.progress_tracker.print_progress(force=True)
            
            self.logger.info("Pipeline completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            self.logger.debug(traceback.format_exc())
            return False


def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(description="TikTok Video Content Extraction Pipeline")
    parser.add_argument("--videos-dir", default="videos", help="Directory containing MP4 files")
    parser.add_argument("--output-dir", default="extracted_content", help="Output directory")
    parser.add_argument("--workers", type=int, default=8, help="Number of concurrent workers")
    parser.add_argument("--batch-size", type=int, default=100, help="Videos per batch")
    parser.add_argument("--max-videos", type=int, help="Maximum videos to process (for testing)")
    parser.add_argument("--no-resume", action="store_true", help="Start fresh (don't resume)")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument("--test", action="store_true", help="Test mode (process 10 videos)")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = getattr(logging, args.log_level.upper())
    setup_logging(level=log_level)
    
    # Test mode
    if args.test:
        args.max_videos = 10
        print("🧪 Running in test mode (10 videos)")
    
    # Create pipeline controller
    controller = VideoPipelineController(
        videos_dir=args.videos_dir,
        output_dir=args.output_dir,
        num_workers=args.workers,
        batch_size=args.batch_size
    )
    
    # Run pipeline
    success = controller.run_pipeline(
        resume=not args.no_resume,
        max_videos=args.max_videos
    )
    
    if success:
        print("✅ Pipeline completed successfully")
        output_file = controller.output_dir / controller.output_csv
        print(f"📄 Results saved to: {output_file}")
        sys.exit(0)
    else:
        print("❌ Pipeline failed")
        sys.exit(1)


if __name__ == "__main__":
    main()