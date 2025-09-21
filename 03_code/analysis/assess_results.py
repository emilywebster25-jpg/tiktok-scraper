#!/usr/bin/env python3
"""Comprehensive assessment of extraction results"""

import pandas as pd
import re
from collections import Counter
import json

# Load results
df = pd.read_csv('extracted_content/video_content_analysis.csv')

print("=== TIKTOK VIDEO CONTENT EXTRACTION RESULTS ===\n")

# 1. Overall Statistics
print("1. OVERALL STATISTICS")
print(f"   Total videos processed: {len(df):,}")
print(f"   Successful (both OCR & audio): {len(df[df['processing_status'] == 'success']):,} ({len(df[df['processing_status'] == 'success'])/len(df)*100:.1f}%)")
print(f"   Partial (either OCR or audio): {len(df[df['processing_status'] == 'partial']):,} ({len(df[df['processing_status'] == 'partial'])/len(df)*100:.1f}%)")
print(f"   Failed: {len(df[df['processing_status'] == 'failed']):,}")

# 2. Audio Transcription Analysis
print("\n2. AUDIO TRANSCRIPTION ANALYSIS")
has_audio = df['spoken_phrases'].notna() & (df['spoken_phrases'] != '')
print(f"   Videos with audio transcription: {has_audio.sum():,} ({has_audio.sum()/len(df)*100:.1f}%)")

# Check audio quality
if has_audio.sum() > 0:
    audio_df = df[has_audio].copy()
    audio_df['word_count'] = audio_df['spoken_phrases'].str.split().str.len()
    print(f"   Average words per transcription: {audio_df['word_count'].mean():.1f}")
    print(f"   Videos with 10+ words: {(audio_df['word_count'] >= 10).sum():,}")
    print(f"   Videos with 50+ words: {(audio_df['word_count'] >= 50).sum():,}")

# 3. OCR Analysis
print("\n3. OCR TEXT EXTRACTION ANALYSIS")
has_ocr = df['on_screen_text'].notna() & (df['on_screen_text'] != '')
print(f"   Videos with OCR text: {has_ocr.sum():,} ({has_ocr.sum()/len(df)*100:.1f}%)")

# Analyze OCR quality
def count_readable_words(text):
    if pd.isna(text):
        return 0
    # Count words that are at least 3 characters and contain letters
    words = re.findall(r'\b[a-zA-Z]{3,}\b', str(text))
    return len(words)

df['readable_ocr_words'] = df['on_screen_text'].apply(count_readable_words)
print(f"   Videos with readable OCR words (3+ chars): {(df['readable_ocr_words'] > 0).sum():,}")
print(f"   Average readable words per video: {df['readable_ocr_words'].mean():.1f}")

# 4. Content Quality Assessment
print("\n4. CONTENT QUALITY ASSESSMENT")
# High quality = has meaningful audio or OCR
has_meaningful_audio = has_audio & (df[has_audio]['spoken_phrases'].str.len() > 50)
has_meaningful_ocr = df['readable_ocr_words'] >= 3
has_meaningful_content = has_meaningful_audio | has_meaningful_ocr

print(f"   Videos with meaningful content: {has_meaningful_content.sum():,} ({has_meaningful_content.sum()/len(df)*100:.1f}%)")
print(f"   - Meaningful audio (50+ chars): {has_meaningful_audio.sum():,}")
print(f"   - Meaningful OCR (3+ words): {has_meaningful_ocr.sum():,}")

# 5. Common Words Analysis
print("\n5. MOST COMMON WORDS IN TRANSCRIPTIONS")
all_words = []
for text in df[has_audio]['spoken_phrases']:
    if pd.notna(text) and len(text) > 10:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        all_words.extend(words)

if all_words:
    word_counts = Counter(all_words)
    # Filter out common words
    stop_words = {'the', 'and', 'you', 'that', 'this', 'for', 'are', 'with', 'have', 'your', 'can', 'get', 'but', 'not', 'all', 'was', 'will', 'just', 'like', 'what', 'out', 'they', 'one', 'would', 'there', 'been', 'more', 'when', 'some', 'than', 'only', 'into', 'very', 'them', 'then', 'come', 'now', 'could', 'here', 'other', 'which', 'their', 'were', 'from', 'each', 'over', 'after', 'down', 'yeah', 'right', 'know', 'gonna', 'wanna', 'let', 'think', 'see', 'make', 'take', 'look', 'want', 'give', 'back', 'because', 'good', 'well', 'how', 'about', 'really', 'going', 'being', 'have', 'need', 'way', 'who', 'why', 'where', 'okay', 'yes', 'got', 'thank'}
    
    fitness_words = [(word, count) for word, count in word_counts.most_common(50) 
                     if word not in stop_words and len(word) > 3][:20]
    
    print("   Top fitness-related words:")
    for word, count in fitness_words:
        print(f"   - {word}: {count}")

# 6. Error Analysis
print("\n6. ERROR PATTERNS")
error_df = df[df['error_notes'].notna() & (df['error_notes'] != '')]
if len(error_df) > 0:
    print(f"   Videos with errors: {len(error_df):,}")
    error_types = Counter()
    for error in error_df['error_notes']:
        if 'Transcription failed' in error:
            error_types['Audio transcription failed'] += 1
        elif 'Frame extraction failed' in error:
            error_types['Frame extraction failed'] += 1
        else:
            error_types['Other'] += 1
    
    for error_type, count in error_types.most_common():
        print(f"   - {error_type}: {count}")

# 7. Sample High-Quality Results
print("\n7. SAMPLE HIGH-QUALITY EXTRACTIONS")
quality_df = df[has_meaningful_content].head(5)
for idx, row in quality_df.iterrows():
    print(f"\n   Video: {row['filename']}")
    if pd.notna(row['spoken_phrases']) and len(row['spoken_phrases']) > 50:
        print(f"   Audio: {row['spoken_phrases'][:150]}...")
    if row['readable_ocr_words'] >= 3:
        print(f"   OCR: {row['on_screen_text'][:150]}...")

# 8. Recommendations
print("\n8. ANALYSIS SUMMARY & RECOMMENDATIONS")
print(f"   ✓ Successfully extracted content from {has_meaningful_content.sum():,} videos ({has_meaningful_content.sum()/len(df)*100:.1f}%)")
print(f"   ✓ Audio transcription working well - {has_meaningful_audio.sum():,} videos with substantial speech")
print(f"   ✗ OCR remains challenging - only {has_meaningful_ocr.sum():,} videos with readable text")
print("\n   Recommendations:")
print("   1. Focus analysis on the ~35% of videos with meaningful content")
print("   2. Audio transcriptions are more reliable than OCR for TikTok fitness content")
print("   3. Consider filtering videos by creator or engagement for higher quality content")
print("   4. Many videos likely contain only music/background audio without instructional speech")