#!/usr/bin/env python3
"""
Generate top performers report with detailed engagement analysis
"""
import os
import json
import csv
from datetime import datetime
from collections import defaultdict

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APIFY_DIR = os.path.join(BASE_DIR, "apify_downloads")
OUTPUT_DIR = os.path.join(BASE_DIR, "exports")

def calculate_metrics(video_data):
    """Calculate various engagement metrics"""
    likes = video_data.get('diggCount', 0)
    comments = video_data.get('commentCount', 0)
    shares = video_data.get('shareCount', 0)
    views = video_data.get('playCount', 1)
    
    engagement_rate = ((likes + comments + shares) / views * 100) if views > 0 else 0
    viral_score = (shares / views * 100) if views > 0 else 0
    comment_rate = (comments / views * 100) if views > 0 else 0
    
    return {
        'engagement_rate': engagement_rate,
        'viral_score': viral_score,
        'comment_rate': comment_rate,
        'total_engagement': likes + comments + shares
    }

def main():
    print("🏆 Generating Top Performers Report...")
    
    all_videos = []
    
    # Process all JSON files
    json_files = [f for f in os.listdir(APIFY_DIR) if f.endswith('.json') and f.startswith('tiktok_')]
    
    for json_file in sorted(json_files):
        # Extract search query
        search_query = json_file[7:]  # Remove 'tiktok_'
        search_query = '_'.join(search_query.split('_')[:-2])  # Remove timestamp
        search_query = search_query.replace('_', ' ')
        
        json_path = os.path.join(APIFY_DIR, json_file)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for video_data in data:
                    if video_data.get('playCount', 0) > 1000:  # Filter for videos with decent views
                        metrics = calculate_metrics(video_data)
                        
                        video_info = {
                            'video_id': video_data.get('id', ''),
                            'caption': video_data.get('text', '')[:100],  # First 100 chars
                            'creator': video_data.get('authorMeta', {}).get('name', ''),
                            'creator_followers': video_data.get('authorMeta', {}).get('fans', 0),
                            'search_query': search_query,
                            'views': video_data.get('playCount', 0),
                            'likes': video_data.get('diggCount', 0),
                            'comments': video_data.get('commentCount', 0),
                            'shares': video_data.get('shareCount', 0),
                            'engagement_rate': metrics['engagement_rate'],
                            'viral_score': metrics['viral_score'],
                            'comment_rate': metrics['comment_rate'],
                            'total_engagement': metrics['total_engagement'],
                            'duration': video_data.get('videoMeta', {}).get('duration', 0),
                            'create_date': video_data.get('createTimeISO', '')[:10],
                            'url': video_data.get('webVideoUrl', '')
                        }
                        all_videos.append(video_info)
        
        except Exception as e:
            print(f"⚠️  Error processing {json_file}: {e}")
    
    # Generate multiple reports
    
    # 1. Top 100 by engagement rate
    print("\n📊 Top Videos by Engagement Rate")
    by_engagement = sorted(all_videos, key=lambda x: x['engagement_rate'], reverse=True)[:100]
    
    engagement_file = os.path.join(OUTPUT_DIR, f'top_100_engagement_rate_{datetime.now().strftime("%Y%m%d")}.csv')
    fieldnames = ['rank', 'creator', 'caption', 'engagement_rate', 'views', 'likes', 'comments', 'shares', 
                  'search_query', 'create_date', 'url']
    
    with open(engagement_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i, video in enumerate(by_engagement, 1):
            row = {'rank': i}
            row.update({k: video[k] for k in fieldnames[1:]})
            writer.writerow(row)
    
    print(f"✅ Saved: {engagement_file}")
    
    # 2. Top 100 by viral score (share rate)
    print("\n🚀 Top Videos by Viral Score")
    by_viral = sorted(all_videos, key=lambda x: x['viral_score'], reverse=True)[:100]
    
    viral_file = os.path.join(OUTPUT_DIR, f'top_100_viral_score_{datetime.now().strftime("%Y%m%d")}.csv')
    fieldnames = ['rank', 'creator', 'caption', 'viral_score', 'shares', 'views', 'engagement_rate', 
                  'search_query', 'create_date', 'url']
    
    with open(viral_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i, video in enumerate(by_viral, 1):
            row = {'rank': i}
            row.update({k: video[k] for k in fieldnames[1:]})
            writer.writerow(row)
    
    print(f"✅ Saved: {viral_file}")
    
    # 3. Top videos by search query
    print("\n🔍 Best Videos per Search Query")
    by_query = defaultdict(list)
    for video in all_videos:
        by_query[video['search_query']].append(video)
    
    query_best = []
    for query, videos in by_query.items():
        if videos:
            best = max(videos, key=lambda x: x['engagement_rate'])
            best['query_video_count'] = len(videos)
            query_best.append(best)
    
    query_file = os.path.join(OUTPUT_DIR, f'best_videos_by_search_{datetime.now().strftime("%Y%m%d")}.csv')
    fieldnames = ['search_query', 'query_video_count', 'creator', 'caption', 'engagement_rate', 
                  'views', 'likes', 'url']
    
    with open(query_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for video in sorted(query_best, key=lambda x: x['engagement_rate'], reverse=True):
            writer.writerow({k: video[k] for k in fieldnames})
    
    print(f"✅ Saved: {query_file}")
    
    # 4. Summary statistics
    print("\n📈 Summary Statistics:")
    print(f"   Total videos analyzed: {len(all_videos):,}")
    print(f"   Average engagement rate: {sum(v['engagement_rate'] for v in all_videos) / len(all_videos):.2f}%")
    print(f"   Average views: {sum(v['views'] for v in all_videos) / len(all_videos):,.0f}")
    print(f"   Videos with >10% engagement: {len([v for v in all_videos if v['engagement_rate'] > 10]):,}")
    print(f"   Videos with >1M views: {len([v for v in all_videos if v['views'] > 1000000]):,}")
    
    # Print top 5 for quick reference
    print("\n🌟 Top 5 Videos by Engagement:")
    for i, video in enumerate(by_engagement[:5], 1):
        print(f"   {i}. {video['creator']} ({video['engagement_rate']:.1f}%) - {video['caption'][:50]}...")

if __name__ == "__main__":
    main()