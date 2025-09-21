#!/usr/bin/env python3
"""Investigate why extraction failed"""

import pandas as pd
import json
import os
from collections import Counter

# Load results
df = pd.read_csv('extracted_content/video_content_analysis.csv')

print("=== FAILURE ANALYSIS ===\n")

# 1. Check error notes
print("1. Error patterns:")
error_counts = df['error_notes'].value_counts()
for error, count in error_counts.items():
    if pd.notna(error) and error.strip():
        print(f"   {error[:100]}: {count} videos")

# 2. Analyze confidence scores
print("\n2. Confidence scores:")
print(f"   OCR confidence - Mean: {df['ocr_confidence'].mean():.1f}, Non-zero: {(df['ocr_confidence'] > 0).sum()}")
print(f"   Audio confidence - Mean: {df['transcription_confidence'].mean():.1f}, Non-zero: {(df['transcription_confidence'] > 0).sum()}")

# 3. Check file sizes and durations
print("\n3. Video characteristics:")
print(f"   Duration - Mean: {df['duration_seconds'].mean():.1f}s, Min: {df['duration_seconds'].min():.1f}s, Max: {df['duration_seconds'].max():.1f}s")
print(f"   Videos < 5 seconds: {(df['duration_seconds'] < 5).sum()}")
print(f"   Videos > 60 seconds: {(df['duration_seconds'] > 60).sum()}")

# 4. Sample specific issues
print("\n4. Checking specific failure types:")

# Videos with "tensor" errors (audio issues)
tensor_errors = df[df['spoken_phrases'].astype(str).str.contains('tensor', na=False)]
print(f"   Videos with tensor errors: {len(tensor_errors)}")

# Empty extractions
empty_ocr = df[df['on_screen_text'].isna() | (df['on_screen_text'] == '')]
empty_audio = df[df['spoken_phrases'].isna() | (df['spoken_phrases'] == '')]
print(f"   Videos with no OCR text: {len(empty_ocr)}")
print(f"   Videos with no audio text: {len(empty_audio)}")

# 5. Find a few good examples to test with
print("\n5. Finding test candidates:")
# Get videos with reasonable duration and partial success
test_candidates = df[
    (df['duration_seconds'] > 10) & 
    (df['duration_seconds'] < 120) &
    (df['processing_status'] == 'partial')
].head(10)

print(f"   Found {len(test_candidates)} test candidates")
for _, video in test_candidates.iterrows():
    print(f"   - {video['filename']} ({video['duration_seconds']:.1f}s)")

# Save test video list
with open('test_videos.txt', 'w') as f:
    for _, video in test_candidates.iterrows():
        f.write(f"{video['filename']}\n")