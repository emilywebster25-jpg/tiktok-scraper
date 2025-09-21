#!/usr/bin/env python3
"""
Data Merger for TikTok Video Content Pipeline

Combines OCR and transcription results into structured CSV output.
Handles data validation and formatting for analysis.

Author: TikTok Content Analysis Pipeline
Created: January 3, 2025
"""

import os
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
import json
from datetime import datetime
import pandas as pd


class DataMerger:
    """
    Merges OCR and transcription results into structured output format.
    
    Features:
    - CSV output with standardized schema
    - Data validation and cleaning
    - Progress tracking and resume capability
    - Error handling and reporting
    """
    
    def __init__(self, output_dir: str = "extracted_content"):
        """
        Initialize data merger.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Define CSV schema
        self.csv_columns = [
            'video_id',
            'filename', 
            'duration_seconds',
            'frame_count',
            'on_screen_text',
            'spoken_phrases',
            'text_timestamps',
            'audio_timestamps',
            'ocr_confidence',
            'transcription_confidence',
            'processing_status',
            'error_notes',
            'processed_timestamp'
        ]
        
    def create_video_record(self, 
                          video_id: str,
                          filename: str,
                          video_metadata: Dict,
                          ocr_results: Dict,
                          transcription_results: Dict) -> Dict[str, Any]:
        """
        Create a standardized record for a video.
        
        Args:
            video_id: Unique video identifier
            filename: Original filename
            video_metadata: Video file metadata
            ocr_results: OCR processing results
            transcription_results: Audio transcription results
            
        Returns:
            Dictionary with standardized video record
        """
        # Determine processing status
        ocr_success = ocr_results.get('error') is None
        transcription_success = transcription_results.get('error') is None
        
        if ocr_success and transcription_success:
            status = 'success'
        elif ocr_success or transcription_success:
            status = 'partial'
        else:
            status = 'failed'
        
        # Collect error notes
        error_notes = []
        if ocr_results.get('error'):
            error_notes.append(f"OCR: {ocr_results['error']}")
        if transcription_results.get('error'):
            error_notes.append(f"Audio: {transcription_results['error']}")
        
        # Create record
        record = {
            'video_id': video_id,
            'filename': filename,
            'duration_seconds': round(video_metadata.get('duration', 0), 2),
            'frame_count': ocr_results.get('total_frames_processed', 0),
            'on_screen_text': self._clean_text_for_csv(ocr_results.get('deduplicated_text', '')),
            'spoken_phrases': self._clean_text_for_csv(transcription_results.get('text', '')),
            'text_timestamps': self._clean_text_for_csv(ocr_results.get('text_with_timestamps', '')),
            'audio_timestamps': self._clean_text_for_csv(transcription_results.get('word_timestamps', '')),
            'ocr_confidence': round(ocr_results.get('average_confidence', 0), 2),
            'transcription_confidence': round(transcription_results.get('confidence', 0), 2),
            'processing_status': status,
            'error_notes': '; '.join(error_notes),
            'processed_timestamp': datetime.now().isoformat()
        }
        
        return record
    
    def _clean_text_for_csv(self, text: str) -> str:
        """
        Clean text for CSV output.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text safe for CSV
        """
        if not text:
            return ''
        
        # Remove newlines and normalize whitespace
        cleaned = ' '.join(text.split())
        
        # Escape quotes and commas for CSV safety
        cleaned = cleaned.replace('"', '""')
        
        # Limit length to prevent CSV issues
        max_length = 2000
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + '...'
        
        return cleaned
    
    def append_to_csv(self, record: Dict[str, Any], csv_file: str) -> bool:
        """
        Append a record to CSV file.
        
        Args:
            record: Video record dictionary
            csv_file: Path to CSV file
            
        Returns:
            True if successful
        """
        try:
            csv_path = self.output_dir / csv_file
            
            # Check if file exists and has headers
            write_headers = not csv_path.exists()
            
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_columns)
                
                if write_headers:
                    writer.writeheader()
                
                writer.writerow(record)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing to CSV {csv_file}: {e}")
            return False
    
    def create_batch_summary(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create summary statistics for a batch of records.
        
        Args:
            records: List of video records
            
        Returns:
            Summary statistics dictionary
        """
        if not records:
            return {}
        
        total_videos = len(records)
        successful = len([r for r in records if r['processing_status'] == 'success'])
        partial = len([r for r in records if r['processing_status'] == 'partial'])
        failed = len([r for r in records if r['processing_status'] == 'failed'])
        
        # Calculate averages for successful processing
        success_records = [r for r in records if r['processing_status'] in ['success', 'partial']]
        
        if success_records:
            avg_duration = sum(r['duration_seconds'] for r in success_records) / len(success_records)
            avg_frames = sum(r['frame_count'] for r in success_records) / len(success_records)
            avg_ocr_conf = sum(r['ocr_confidence'] for r in success_records if r['ocr_confidence'] > 0)
            avg_ocr_conf = avg_ocr_conf / len([r for r in success_records if r['ocr_confidence'] > 0]) if avg_ocr_conf else 0
            avg_trans_conf = sum(r['transcription_confidence'] for r in success_records if r['transcription_confidence'] > 0)
            avg_trans_conf = avg_trans_conf / len([r for r in success_records if r['transcription_confidence'] > 0]) if avg_trans_conf else 0
        else:
            avg_duration = avg_frames = avg_ocr_conf = avg_trans_conf = 0
        
        # Text extraction statistics
        videos_with_text = len([r for r in records if r['on_screen_text']])
        videos_with_audio = len([r for r in records if r['spoken_phrases']])
        
        summary = {
            'batch_timestamp': datetime.now().isoformat(),
            'total_videos': total_videos,
            'successful_processing': successful,
            'partial_processing': partial,
            'failed_processing': failed,
            'success_rate': round(successful / total_videos * 100, 1) if total_videos > 0 else 0,
            'avg_video_duration': round(avg_duration, 2),
            'avg_frames_per_video': round(avg_frames, 1),
            'avg_ocr_confidence': round(avg_ocr_conf, 1),
            'avg_transcription_confidence': round(avg_trans_conf, 2),
            'videos_with_text': videos_with_text,
            'videos_with_audio': videos_with_audio,
            'text_extraction_rate': round(videos_with_text / total_videos * 100, 1) if total_videos > 0 else 0,
            'audio_extraction_rate': round(videos_with_audio / total_videos * 100, 1) if total_videos > 0 else 0
        }
        
        return summary
    
    def save_batch_summary(self, summary: Dict[str, Any], summary_file: str = "processing_summary.json") -> bool:
        """
        Save batch summary to JSON file.
        
        Args:
            summary: Summary dictionary
            summary_file: Output filename
            
        Returns:
            True if successful
        """
        try:
            summary_path = self.output_dir / summary_file
            
            # Load existing summaries if file exists
            existing_summaries = []
            if summary_path.exists():
                try:
                    with open(summary_path, 'r') as f:
                        existing_summaries = json.load(f)
                        if not isinstance(existing_summaries, list):
                            existing_summaries = [existing_summaries]
                except json.JSONDecodeError:
                    self.logger.warning(f"Corrupted summary file {summary_file}, starting fresh")
                    existing_summaries = []
            
            # Append new summary
            existing_summaries.append(summary)
            
            # Save updated summaries
            with open(summary_path, 'w') as f:
                json.dump(existing_summaries, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving summary to {summary_file}: {e}")
            return False
    
    def load_existing_csv(self, csv_file: str) -> pd.DataFrame:
        """
        Load existing CSV file as DataFrame.
        
        Args:
            csv_file: CSV filename
            
        Returns:
            DataFrame with existing data
        """
        try:
            csv_path = self.output_dir / csv_file
            
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                self.logger.info(f"Loaded {len(df)} existing records from {csv_file}")
                return df
            else:
                return pd.DataFrame(columns=self.csv_columns)
                
        except Exception as e:
            self.logger.error(f"Error loading CSV {csv_file}: {e}")
            return pd.DataFrame(columns=self.csv_columns)
    
    def get_processed_video_ids(self, csv_file: str) -> set:
        """
        Get set of video IDs that have already been processed.
        
        Args:
            csv_file: CSV filename
            
        Returns:
            Set of processed video IDs
        """
        try:
            df = self.load_existing_csv(csv_file)
            if 'video_id' in df.columns:
                return set(df['video_id'].astype(str))
            else:
                return set()
        except Exception as e:
            self.logger.error(f"Error reading processed video IDs: {e}")
            return set()
    
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a video record for completeness and correctness.
        
        Args:
            record: Video record dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        required_fields = ['video_id', 'filename', 'processing_status']
        for field in required_fields:
            if field not in record or not record[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate data types
        if 'duration_seconds' in record:
            try:
                float(record['duration_seconds'])
            except (ValueError, TypeError):
                errors.append("Invalid duration_seconds: must be numeric")
        
        if 'frame_count' in record:
            try:
                int(record['frame_count'])
            except (ValueError, TypeError):
                errors.append("Invalid frame_count: must be integer")
        
        # Validate processing status
        valid_statuses = ['success', 'partial', 'failed']
        if record.get('processing_status') not in valid_statuses:
            errors.append(f"Invalid processing_status: must be one of {valid_statuses}")
        
        return len(errors) == 0, errors


def main():
    """Test the data merger with sample data."""
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create sample data for testing
    merger = DataMerger()
    
    # Sample video metadata
    video_metadata = {
        'duration': 25.5,
        'width': 576,
        'height': 1024,
        'fps': 30
    }
    
    # Sample OCR results
    ocr_results = {
        'deduplicated_text': 'WORKOUT TIME; 20 MIN HIIT',
        'text_with_timestamps': '3.0s:WORKOUT TIME; 6.0s:20 MIN HIIT',
        'total_frames_processed': 8,
        'average_confidence': 85.5,
        'error': None
    }
    
    # Sample transcription results
    transcription_results = {
        'text': 'Welcome to this twenty minute high intensity interval training workout',
        'word_timestamps': '0.5s-Welcome;1.2s-to;1.5s-this;2.0s-twenty;2.5s-minute',
        'confidence': 0.92,
        'error': None
    }
    
    # Create record
    record = merger.create_video_record(
        video_id='test_123',
        filename='test_video.mp4',
        video_metadata=video_metadata,
        ocr_results=ocr_results,
        transcription_results=transcription_results
    )
    
    print("Sample record:")
    for key, value in record.items():
        print(f"  {key}: {value}")
    
    # Validate record
    is_valid, errors = merger.validate_record(record)
    print(f"\nRecord valid: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    # Save to CSV
    success = merger.append_to_csv(record, 'test_output.csv')
    print(f"CSV save successful: {success}")
    
    # Create and save summary
    summary = merger.create_batch_summary([record])
    print(f"\nBatch summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    merger.save_batch_summary(summary, 'test_summary.json')


if __name__ == "__main__":
    main()