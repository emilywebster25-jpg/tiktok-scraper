#!/usr/bin/env python3
"""Export high-quality content for further analysis"""

import pandas as pd
import re

# Load results
df = pd.read_csv('extracted_content/video_content_analysis.csv')

# Define quality criteria
def has_meaningful_audio(row):
    """Check if audio transcription has meaningful content"""
    if pd.isna(row['spoken_phrases']) or row['spoken_phrases'] == '':
        return False
    # At least 50 characters and 10 words
    text = str(row['spoken_phrases'])
    words = text.split()
    return len(text) > 50 and len(words) >= 10

def has_fitness_keywords(text):
    """Check if text contains fitness-related keywords"""
    if pd.isna(text):
        return False
    text_lower = str(text).lower()
    fitness_keywords = [
        'workout', 'exercise', 'reps', 'sets', 'seconds', 'minutes',
        'squat', 'lunge', 'plank', 'push', 'pull', 'core', 'abs',
        'cardio', 'strength', 'hiit', 'pilates', 'yoga', 'barre',
        'burn', 'sweat', 'muscle', 'body', 'fitness', 'train',
        'repeat', 'rest', 'round', 'circuit'
    ]
    return any(keyword in text_lower for keyword in fitness_keywords)

# Filter for quality content
df['has_meaningful_audio'] = df.apply(has_meaningful_audio, axis=1)
df['has_fitness_content'] = df['spoken_phrases'].apply(has_fitness_keywords)

# Get high-quality subset
quality_df = df[df['has_meaningful_audio'] & df['has_fitness_content']].copy()

print(f"Found {len(quality_df)} videos with high-quality fitness content")
print(f"This represents {len(quality_df)/len(df)*100:.1f}% of all videos")

# Add search query from filename
def extract_search_query(filename):
    """Extract search query from filename"""
    # Pattern: search_query_creator_id.mp4
    parts = filename.replace('.mp4', '').split('_')
    if len(parts) > 2:
        # Join all parts except creator and ID
        return '_'.join(parts[:-2])
    return 'unknown'

quality_df['search_query'] = quality_df['filename'].apply(extract_search_query)

# Export quality content
quality_df[['video_id', 'filename', 'search_query', 'duration_seconds', 'spoken_phrases', 'on_screen_text']].to_csv(
    'extracted_content/high_quality_fitness_content.csv', 
    index=False
)

print(f"\nExported to: extracted_content/high_quality_fitness_content.csv")

# Show distribution by search query
print("\nContent distribution by search query:")
query_counts = quality_df['search_query'].value_counts().head(20)
for query, count in query_counts.items():
    print(f"  {query}: {count} videos")

# Sample content
print("\n=== SAMPLE HIGH-QUALITY CONTENT ===")
for _, row in quality_df.head(3).iterrows():
    print(f"\nVideo: {row['filename']}")
    print(f"Duration: {row['duration_seconds']:.1f} seconds")
    print(f"Transcription: {row['spoken_phrases'][:200]}...")