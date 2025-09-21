#!/usr/bin/env python3
"""
Export clean TikTok video data - filtering out unknown/error entries
"""
import os
import json
import csv
from datetime import datetime
import re

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APIFY_DIR = os.path.join(BASE_DIR, "apify_downloads")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
OUTPUT_DIR = os.path.join(BASE_DIR, "exports")

def extract_hashtags(text):
    """Extract hashtags from video text"""
    return ' '.join(re.findall(r'#\w+', text))

def calculate_engagement_rate(video_data):
    """Calculate engagement rate (likes + comments + shares) / views"""
    likes = video_data.get('diggCount', 0)
    comments = video_data.get('commentCount', 0)
    shares = video_data.get('shareCount', 0)
    views = video_data.get('playCount', 1)
    
    if views > 0:
        return ((likes + comments + shares) / views) * 100
    return 0

def is_valid_search_query(query):
    """Check if search query is valid (not unknown or error-like)"""
    if not query or query.lower() in ['unknown', 'unknown_search', '']:
        return False
    if len(query) < 3:  # Too short
        return False
    if query.startswith('tiktok_') or query.endswith('.json'):  # Filename artifacts
        return False
    return True

def process_video_data(video_data, search_query):
    """Extract relevant fields from video data"""
    author_meta = video_data.get('authorMeta', {})
    video_meta = video_data.get('videoMeta', {})
    music_meta = video_data.get('musicMeta', {})
    
    # Basic quality checks
    if not video_data.get('id'):
        return None
    if not author_meta.get('name'):
        return None
    if video_data.get('playCount', 0) < 10:  # Filter very low view videos
        return None
    
    return {
        'video_id': video_data.get('id', ''),
        'search_query': search_query,
        'caption': video_data.get('text', ''),
        'hashtags': extract_hashtags(video_data.get('text', '')),
        'create_time': video_data.get('createTimeISO', ''),
        
        # Creator info
        'creator_username': author_meta.get('name', ''),
        'creator_nickname': author_meta.get('nickName', ''),
        'creator_followers': author_meta.get('fans', 0),
        'creator_verified': author_meta.get('verified', False),
        
        # Engagement metrics
        'views': video_data.get('playCount', 0),
        'likes': video_data.get('diggCount', 0),
        'comments': video_data.get('commentCount', 0),
        'shares': video_data.get('shareCount', 0),
        'engagement_rate': calculate_engagement_rate(video_data),
        
        # Video details
        'duration_seconds': video_meta.get('duration', 0),
        'video_url': video_data.get('webVideoUrl', ''),
        'music_name': music_meta.get('musicName', ''),
        
        # Local file info
        'has_local_video': False,
        'local_video_filename': ''
    }

def main():
    print("🧹 Starting clean TikTok video data export...")
    
    all_videos = []
    video_ids_processed = set()
    skipped_unknown = 0
    skipped_invalid = 0
    
    # Create video file lookup
    video_files = {}
    for filename in os.listdir(VIDEOS_DIR):
        if filename.endswith('.mp4'):
            parts = filename.rsplit('_', 1)
            if len(parts) == 2:
                video_id = parts[1].replace('.mp4', '')
                video_files[video_id] = filename
    
    print(f"📹 Found {len(video_files)} local video files")
    
    # Process JSON files with stricter filtering
    json_files = [f for f in os.listdir(APIFY_DIR) 
                  if f.endswith('.json') and f.startswith('tiktok_') and 'unknown' not in f.lower()]
    
    print(f"📂 Processing {len(json_files)} JSON files (excluding unknown files)")
    
    for json_file in sorted(json_files):
        # Extract search query
        if json_file.startswith('tiktok_') and json_file.endswith('.json'):
            search_query = json_file[7:]  # Remove 'tiktok_'
            search_query = '_'.join(search_query.split('_')[:-2])  # Remove timestamp
            search_query = search_query.replace('_', ' ')
        else:
            continue
        
        # Skip if not a valid search query
        if not is_valid_search_query(search_query):
            skipped_unknown += 1
            continue
        
        json_path = os.path.join(APIFY_DIR, json_file)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for video_data in data:
                    video_id = video_data.get('id', '')
                    if video_id and video_id not in video_ids_processed:
                        video_info = process_video_data(video_data, search_query)
                        
                        if video_info:  # Only add if valid
                            # Check if we have local video
                            if video_id in video_files:
                                video_info['has_local_video'] = True
                                video_info['local_video_filename'] = video_files[video_id]
                            
                            all_videos.append(video_info)
                            video_ids_processed.add(video_id)
                        else:
                            skipped_invalid += 1
        
        except Exception as e:
            print(f"⚠️  Error processing {json_file}: {e}")
    
    print(f"✅ Processed {len(all_videos)} valid videos")
    print(f"⏭️  Skipped {skipped_unknown} files with unknown queries")
    print(f"⏭️  Skipped {skipped_invalid} invalid video entries")
    
    # Sort by engagement rate
    all_videos.sort(key=lambda x: x['engagement_rate'], reverse=True)
    
    # Write clean CSV
    output_file = os.path.join(OUTPUT_DIR, f'tiktok_videos_clean_{datetime.now().strftime("%Y%m%d")}.csv')
    
    fieldnames = [
        'video_id', 'search_query', 'caption', 'hashtags', 'create_time',
        'creator_username', 'creator_nickname', 'creator_followers', 'creator_verified',
        'views', 'likes', 'comments', 'shares', 'engagement_rate',
        'duration_seconds', 'video_url', 'music_name',
        'has_local_video', 'local_video_filename'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_videos)
    
    print(f"✅ Clean export complete! File saved to: {output_file}")
    print(f"📊 Summary:")
    print(f"   Clean videos: {len(all_videos):,}")
    print(f"   Videos with local files: {len([v for v in all_videos if v['has_local_video']]):,}")
    print(f"   Average engagement rate: {sum(v['engagement_rate'] for v in all_videos) / len(all_videos):.2f}%")
    
    print(f"\n📈 Top 5 videos by engagement rate:")
    for i, video in enumerate(all_videos[:5], 1):
        print(f"   {i}. {video['creator_username']} - {video['engagement_rate']:.2f}% - {video['caption'][:50]}...")

if __name__ == "__main__":
    main()