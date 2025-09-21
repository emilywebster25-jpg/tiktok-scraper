#!/usr/bin/env python3
"""Analyze the quality of extracted content"""

import pandas as pd
import re

# Load the CSV
df = pd.read_csv('extracted_content/video_content_analysis.csv')

print(f"Total videos processed: {len(df)}")
print(f"Successful: {len(df[df['processing_status'] == 'success'])}")
print(f"Partial: {len(df[df['processing_status'] == 'partial'])}")
print(f"Failed: {len(df[df['processing_status'] == 'failed'])}")

# Analyze text quality
def has_readable_text(text):
    if pd.isna(text) or text == '':
        return False
    # Check if text has at least 3 consecutive readable words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', str(text))
    return len(words) >= 3

# Check OCR quality
ocr_readable = df['on_screen_text'].apply(has_readable_text)
print(f"\nVideos with readable OCR text: {ocr_readable.sum()} ({ocr_readable.sum()/len(df)*100:.1f}%)")

# Check audio transcription quality  
audio_readable = df['spoken_phrases'].apply(has_readable_text)
print(f"Videos with readable audio transcription: {audio_readable.sum()} ({audio_readable.sum()/len(df)*100:.1f}%)")

# Find best examples
readable_mask = ocr_readable | audio_readable
if readable_mask.sum() > 0:
    print(f"\nTotal videos with ANY readable content: {readable_mask.sum()} ({readable_mask.sum()/len(df)*100:.1f}%)")
    
    # Show some examples
    print("\n=== Sample of videos with readable content ===")
    readable_df = df[readable_mask].head(5)
    for idx, row in readable_df.iterrows():
        print(f"\nVideo: {row['filename']}")
        if has_readable_text(row['on_screen_text']):
            print(f"OCR: {row['on_screen_text'][:100]}...")
        if has_readable_text(row['spoken_phrases']):
            print(f"Audio: {row['spoken_phrases'][:100]}...")