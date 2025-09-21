#!/usr/bin/env python3
"""
OCR Processor for TikTok Video Content Pipeline

Extracts text from video frames using Tesseract OCR.
Optimized for social media text overlays with deduplication.

Author: TikTok Content Analysis Pipeline
Created: January 3, 2025
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
from difflib import SequenceMatcher

import cv2
import pytesseract
from PIL import Image
import numpy as np


class OCRProcessor:
    """
    Processes video frames to extract text using Tesseract OCR.
    
    Features:
    - Text preprocessing for social media content
    - Confidence-based filtering
    - Duplicate text detection across frames
    - Timestamp association
    """
    
    def __init__(self, 
                 confidence_threshold: int = 30,
                 similarity_threshold: float = 0.8,
                 tesseract_config: str = '--psm 8 --oem 3'):
        """
        Initialize OCR processor.
        
        Args:
            confidence_threshold: Minimum OCR confidence (0-100)
            similarity_threshold: Text similarity threshold for deduplication
            tesseract_config: Tesseract configuration string
        """
        self.confidence_threshold = confidence_threshold
        self.similarity_threshold = similarity_threshold
        self.tesseract_config = tesseract_config
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Test Tesseract installation
        try:
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"Using Tesseract version: {version}")
        except Exception as e:
            self.logger.error(f"Tesseract not found or not working: {e}")
            raise
            
    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image as numpy array or None if error
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Could not load image: {image_path}")
                return None
                
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Scale up image for better OCR (TikTok text is often small)
            height, width = gray.shape
            scale_factor = 2.0  # 2x scaling
            scaled = cv2.resize(gray, (int(width * scale_factor), int(height * scale_factor)), interpolation=cv2.INTER_CUBIC)
            
            # Apply slight Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(scaled, (3, 3), 0)
            
            # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(blurred)
            
            # Try multiple thresholding approaches and pick the best one
            # Approach 1: Otsu's method
            _, binary1 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Approach 2: Adaptive thresholding
            binary2 = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # Approach 3: Simple threshold for high contrast text
            _, binary3 = cv2.threshold(enhanced, 127, 255, cv2.THRESH_BINARY)
            
            # For TikTok videos, often white text on dark background, so try inverted too
            _, binary4 = cv2.threshold(enhanced, 127, 255, cv2.THRESH_BINARY_INV)
            
            # Return the original enhanced grayscale - let Tesseract handle the thresholding
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Error preprocessing image {image_path}: {e}")
            return None
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, any]:
        """
        Extract text from a single image using OCR.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                return {
                    'text': '',
                    'confidence': 0,
                    'word_count': 0,
                    'bounding_boxes': [],
                    'error': 'Image preprocessing failed'
                }
            
            # Run OCR with detailed output
            try:
                ocr_data = pytesseract.image_to_data(
                    processed_image, 
                    config=self.tesseract_config,
                    output_type=pytesseract.Output.DICT
                )
            except Exception as e:
                self.logger.error(f"Tesseract OCR failed for {image_path}: {e}")
                return {
                    'text': '',
                    'confidence': 0,
                    'word_count': 0,
                    'bounding_boxes': [],
                    'error': f'OCR failed: {e}'
                }
            
            # Filter text by confidence and extract valid words
            valid_words = []
            word_confidences = []
            bounding_boxes = []
            
            for i, confidence in enumerate(ocr_data['conf']):
                if confidence > self.confidence_threshold:
                    text = ocr_data['text'][i].strip()
                    if text and len(text) > 1:  # Ignore single characters
                        valid_words.append(text)
                        word_confidences.append(confidence)
                        
                        # Store bounding box
                        bbox = {
                            'x': ocr_data['left'][i],
                            'y': ocr_data['top'][i],
                            'width': ocr_data['width'][i],
                            'height': ocr_data['height'][i]
                        }
                        bounding_boxes.append(bbox)
            
            # Combine words into text
            extracted_text = ' '.join(valid_words)
            
            # Clean up text
            cleaned_text = self._clean_text(extracted_text)
            
            # Calculate average confidence
            avg_confidence = np.mean(word_confidences) if word_confidences else 0
            
            return {
                'text': cleaned_text,
                'confidence': float(avg_confidence),
                'word_count': len(valid_words),
                'bounding_boxes': bounding_boxes,
                'raw_text': extracted_text,
                'error': None
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in OCR for {image_path}: {e}")
            return {
                'text': '',
                'confidence': 0,
                'word_count': 0,
                'bounding_boxes': [],
                'error': f'Unexpected error: {e}'
            }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ''
            
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove obvious OCR artifacts (single characters separated by spaces)
        words = cleaned.split()
        filtered_words = []
        
        for word in words:
            # Keep words that are at least 2 characters or are common single-letter words/numbers
            if len(word) >= 2 or word.lower() in ['i', 'a'] or word.isdigit():
                filtered_words.append(word)
        
        return ' '.join(filtered_words)
    
    def process_frame_sequence(self, frame_files: List[str], timestamps: List[float]) -> Dict[str, any]:
        """
        Process a sequence of frames and deduplicate text.
        
        Args:
            frame_files: List of frame file paths
            timestamps: Corresponding timestamps for each frame
            
        Returns:
            Dictionary with deduplicated text and timing information
        """
        if len(frame_files) != len(timestamps):
            raise ValueError("Frame files and timestamps must have same length")
        
        all_extractions = []
        
        # Process each frame
        for frame_file, timestamp in zip(frame_files, timestamps):
            self.logger.debug(f"Processing frame: {frame_file}")
            
            extraction = self.extract_text_from_image(frame_file)
            extraction['timestamp'] = timestamp
            extraction['frame_file'] = frame_file
            
            all_extractions.append(extraction)
        
        # Deduplicate text across frames
        deduplicated_text = self._deduplicate_text_sequence(all_extractions)
        
        # Aggregate results
        total_frames = len(frame_files)
        successful_frames = len([e for e in all_extractions if e['error'] is None])
        total_words = sum(e['word_count'] for e in all_extractions)
        avg_confidence = np.mean([e['confidence'] for e in all_extractions if e['confidence'] > 0])
        
        return {
            'deduplicated_text': deduplicated_text,
            'text_with_timestamps': self._create_timestamped_text(all_extractions),
            'total_frames_processed': total_frames,
            'successful_frames': successful_frames,
            'total_words_found': total_words,
            'average_confidence': float(avg_confidence) if not np.isnan(avg_confidence) else 0,
            'frame_extractions': all_extractions
        }
    
    def _deduplicate_text_sequence(self, extractions: List[Dict]) -> str:
        """
        Remove duplicate text across frame sequence.
        
        Args:
            extractions: List of extraction results
            
        Returns:
            Deduplicated text string
        """
        unique_texts = []
        
        for extraction in extractions:
            text = extraction.get('text', '').strip()
            if not text:
                continue
                
            # Check if this text is similar to any existing text
            is_duplicate = False
            for existing_text in unique_texts:
                similarity = SequenceMatcher(None, text.lower(), existing_text.lower()).ratio()
                if similarity >= self.similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_texts.append(text)
        
        # Join unique texts with semicolon separator
        return '; '.join(unique_texts)
    
    def _create_timestamped_text(self, extractions: List[Dict]) -> str:
        """
        Create text with timestamp markers.
        
        Args:
            extractions: List of extraction results
            
        Returns:
            Timestamped text string
        """
        timestamped_parts = []
        
        for extraction in extractions:
            text = extraction.get('text', '').strip()
            timestamp = extraction.get('timestamp', 0)
            
            if text:
                timestamped_parts.append(f"{timestamp:.1f}s:{text}")
        
        return '; '.join(timestamped_parts)


def main():
    """Test the OCR processor with sample frames."""
    import sys
    import glob
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) != 2:
        print("Usage: python ocr_processor.py <frames_directory>")
        sys.exit(1)
        
    frames_dir = sys.argv[1]
    
    # Find frame files
    frame_files = glob.glob(os.path.join(frames_dir, "*.png"))
    frame_files.sort()
    
    if not frame_files:
        print(f"No PNG files found in {frames_dir}")
        sys.exit(1)
    
    # Create dummy timestamps
    timestamps = [i * 2.5 for i in range(len(frame_files))]
    
    processor = OCRProcessor()
    results = processor.process_frame_sequence(frame_files, timestamps)
    
    print(f"Processed {results['total_frames_processed']} frames")
    print(f"Successful: {results['successful_frames']}")
    print(f"Total words: {results['total_words_found']}")
    print(f"Average confidence: {results['average_confidence']:.1f}%")
    print(f"Deduplicated text: {results['deduplicated_text']}")
    print(f"Timestamped text: {results['text_with_timestamps']}")


if __name__ == "__main__":
    main()