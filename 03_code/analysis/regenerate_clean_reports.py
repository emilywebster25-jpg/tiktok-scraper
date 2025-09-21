#!/usr/bin/env python3
"""
Regenerate all reports with clean data (no unknowns/errors)
"""
import os
import json
import csv
from datetime import datetime
from collections import Counter, defaultdict
import statistics
import re

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APIFY_DIR = os.path.join(BASE_DIR, "apify_downloads")
OUTPUT_DIR = os.path.join(BASE_DIR, "exports")

def is_valid_search_query(query):
    """Check if search query is valid"""
    if not query or query.lower() in ['unknown', 'unknown_search', '']:
        return False
    if len(query) < 3:
        return False
    if query.startswith('tiktok_') or query.endswith('.json'):
        return False
    return True

def is_valid_video(video_data):
    """Check if video data is valid"""
    if not video_data.get('id'):
        return False
    if not video_data.get('authorMeta', {}).get('name'):
        return False
    if video_data.get('playCount', 0) < 10:
        return False
    return True

def calculate_metrics(video_data):
    """Calculate engagement metrics"""
    likes = video_data.get('diggCount', 0)
    comments = video_data.get('commentCount', 0)
    shares = video_data.get('shareCount', 0)
    views = video_data.get('playCount', 1)
    
    engagement_rate = ((likes + comments + shares) / views * 100) if views > 0 else 0
    viral_score = (shares / views * 100) if views > 0 else 0
    
    return {
        'engagement_rate': engagement_rate,
        'viral_score': viral_score,
        'total_engagement': likes + comments + shares
    }

def extract_hashtags(text):
    """Extract hashtags from text"""
    return [tag.lower() for tag in re.findall(r'#(\w+)', text)]

def main():
    print("🧹 Regenerating all reports with clean data...")
    
    # Collect all clean video data
    all_videos = []
    hashtag_counter = Counter()
    hashtag_stats = defaultdict(lambda: {'videos': 0, 'total_views': 0, 'total_engagement': 0})
    creators = defaultdict(lambda: {
        'videos': [],
        'total_views': 0,
        'total_likes': 0,
        'total_comments': 0,
        'total_shares': 0,
        'followers': 0,
        'verified': False,
        'bio': '',
        'nickname': ''
    })
    query_stats = defaultdict(lambda: {
        'videos': [],
        'total_views': 0,
        'total_engagement': 0,
        'engagement_rates': []
    })
    
    # Process only valid JSON files
    json_files = [f for f in os.listdir(APIFY_DIR) 
                  if f.endswith('.json') and f.startswith('tiktok_') and 'unknown' not in f.lower()]
    
    print(f"📂 Processing {len(json_files)} clean JSON files...")
    
    processed_video_ids = set()
    
    for json_file in sorted(json_files):
        # Extract search query
        search_query = json_file[7:]  # Remove 'tiktok_'
        search_query = '_'.join(search_query.split('_')[:-2])  # Remove timestamp
        search_query_display = search_query.replace('_', ' ')
        
        if not is_valid_search_query(search_query_display):
            continue
        
        json_path = os.path.join(APIFY_DIR, json_file)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for video_data in data:
                    if not is_valid_video(video_data):
                        continue
                    
                    video_id = video_data.get('id', '')
                    if video_id in processed_video_ids:
                        continue
                    processed_video_ids.add(video_id)
                    
                    # Calculate metrics
                    metrics = calculate_metrics(video_data)
                    author_meta = video_data.get('authorMeta', {})
                    
                    # Store video data
                    video_info = {
                        'video_id': video_id,
                        'caption': video_data.get('text', '')[:100],
                        'creator': author_meta.get('name', ''),
                        'creator_followers': author_meta.get('fans', 0),
                        'search_query': search_query_display,
                        'views': video_data.get('playCount', 0),
                        'likes': video_data.get('diggCount', 0),
                        'comments': video_data.get('commentCount', 0),
                        'shares': video_data.get('shareCount', 0),
                        'engagement_rate': metrics['engagement_rate'],
                        'viral_score': metrics['viral_score'],
                        'total_engagement': metrics['total_engagement'],
                        'duration': video_data.get('videoMeta', {}).get('duration', 0),
                        'create_date': video_data.get('createTimeISO', '')[:10],
                        'url': video_data.get('webVideoUrl', '')
                    }
                    all_videos.append(video_info)
                    
                    # Process hashtags
                    hashtags = extract_hashtags(video_data.get('text', ''))
                    for tag in hashtags:
                        hashtag_counter[tag] += 1
                        hashtag_stats[tag]['videos'] += 1
                        hashtag_stats[tag]['total_views'] += video_info['views']
                        hashtag_stats[tag]['total_engagement'] += video_info['total_engagement']
                    
                    # Process creators
                    username = author_meta.get('name', '')
                    if username:
                        creator = creators[username]
                        creator['followers'] = author_meta.get('fans', 0)
                        creator['verified'] = author_meta.get('verified', False)
                        creator['bio'] = author_meta.get('signature', '')
                        creator['nickname'] = author_meta.get('nickName', '')
                        
                        creator['total_views'] += video_info['views']
                        creator['total_likes'] += video_info['likes']
                        creator['total_comments'] += video_info['comments']
                        creator['total_shares'] += video_info['shares']
                        creator['videos'].append(video_info)
                    
                    # Process query stats
                    query_stats[search_query_display]['videos'].append(video_info)
                    query_stats[search_query_display]['total_views'] += video_info['views']
                    query_stats[search_query_display]['total_engagement'] += video_info['total_engagement']
                    query_stats[search_query_display]['engagement_rates'].append(metrics['engagement_rate'])
        
        except Exception as e:
            print(f"⚠️  Error processing {json_file}: {e}")
    
    print(f"✅ Processed {len(all_videos)} clean videos")
    
    # 1. TOP PERFORMERS REPORT
    print("\n🏆 Generating clean top performers...")
    
    # Top 100 by engagement
    by_engagement = sorted(all_videos, key=lambda x: x['engagement_rate'], reverse=True)[:100]
    
    engagement_file = os.path.join(OUTPUT_DIR, f'top_100_engagement_clean_{datetime.now().strftime("%Y%m%d")}.csv')
    fieldnames = ['rank', 'creator', 'caption', 'engagement_rate', 'views', 'likes', 'comments', 'shares', 
                  'search_query', 'create_date', 'url']
    
    with open(engagement_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i, video in enumerate(by_engagement, 1):
            row = {'rank': i}
            row.update({k: video[k] for k in fieldnames[1:]})
            writer.writerow(row)
    
    # Top 100 by viral score
    by_viral = sorted(all_videos, key=lambda x: x['viral_score'], reverse=True)[:100]
    
    viral_file = os.path.join(OUTPUT_DIR, f'top_100_viral_clean_{datetime.now().strftime("%Y%m%d")}.csv')
    fieldnames = ['rank', 'creator', 'caption', 'viral_score', 'shares', 'views', 'engagement_rate', 
                  'search_query', 'create_date', 'url']
    
    with open(viral_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i, video in enumerate(by_viral, 1):
            row = {'rank': i}
            row.update({k: video[k] for k in fieldnames[1:]})
            writer.writerow(row)
    
    # 2. HASHTAG ANALYSIS
    print("\n🏷️  Generating clean hashtag analysis...")
    
    # Calculate hashtag performance
    for tag in hashtag_stats:
        stats = hashtag_stats[tag]
        stats['avg_views'] = stats['total_views'] / stats['videos'] if stats['videos'] > 0 else 0
        stats['avg_engagement'] = stats['total_engagement'] / stats['videos'] if stats['videos'] > 0 else 0
        stats['engagement_rate'] = (stats['total_engagement'] / stats['total_views'] * 100) if stats['total_views'] > 0 else 0
    
    hashtag_file = os.path.join(OUTPUT_DIR, f'hashtag_analysis_clean_{datetime.now().strftime("%Y%m%d")}.csv')
    
    with open(hashtag_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['rank', 'hashtag', 'count', 'videos', 'avg_views', 'avg_engagement', 'engagement_rate'])
        
        for i, (tag, count) in enumerate(hashtag_counter.most_common(100), 1):
            stats = hashtag_stats[tag]
            writer.writerow([
                i, f"#{tag}", count, stats['videos'],
                f"{stats['avg_views']:.0f}",
                f"{stats['avg_engagement']:.0f}",
                f"{stats['engagement_rate']:.2f}%"
            ])
    
    # 3. CREATOR ANALYSIS
    print("\n👥 Generating clean creator analysis...")
    
    creator_stats = []
    for username, data in creators.items():
        video_count = len(data['videos'])
        if video_count > 0:
            avg_engagement = (data['total_likes'] + data['total_comments'] + data['total_shares']) / video_count
            engagement_rate = ((data['total_likes'] + data['total_comments'] + data['total_shares']) / 
                             data['total_views'] * 100) if data['total_views'] > 0 else 0
            
            creator_stats.append({
                'username': username,
                'nickname': data['nickname'],
                'followers': data['followers'],
                'verified': data['verified'],
                'video_count': video_count,
                'total_views': data['total_views'],
                'avg_engagement': avg_engagement,
                'engagement_rate': engagement_rate,
                'bio': data['bio'][:200]
            })
    
    creators_file = os.path.join(OUTPUT_DIR, f'top_creators_clean_{datetime.now().strftime("%Y%m%d")}.csv')
    top_creators = sorted(creator_stats, key=lambda x: x['followers'], reverse=True)[:100]
    
    fieldnames = ['rank', 'username', 'followers', 'video_count', 'engagement_rate', 'avg_engagement', 'verified', 'bio']
    
    with open(creators_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i, creator in enumerate(top_creators, 1):
            row = {'rank': i}
            row.update({k: creator[k] for k in fieldnames[1:]})
            writer.writerow(row)
    
    # 4. SEARCH QUERY ANALYSIS
    print("\n🔍 Generating clean search query analysis...")
    
    query_summary = []
    for query, stats in query_stats.items():
        video_count = len(stats['videos'])
        if video_count > 0:
            avg_engagement_rate = statistics.mean(stats['engagement_rates'])
            high_performers = len([v for v in stats['videos'] if v['engagement_rate'] > 10])
            
            query_summary.append({
                'search_query': query,
                'video_count': video_count,
                'avg_engagement_rate': avg_engagement_rate,
                'high_performers': high_performers,
                'high_performer_pct': (high_performers / video_count * 100)
            })
    
    query_file = os.path.join(OUTPUT_DIR, f'search_queries_clean_{datetime.now().strftime("%Y%m%d")}.csv')
    
    with open(query_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['rank', 'search_query', 'video_count', 'avg_engagement_rate', 'high_performer_pct'])
        writer.writeheader()
        for i, query in enumerate(sorted(query_summary, key=lambda x: x['avg_engagement_rate'], reverse=True), 1):
            row = {'rank': i}
            row.update({k: query[k] for k in ['search_query', 'video_count', 'avg_engagement_rate', 'high_performer_pct']})
            writer.writerow(row)
    
    print(f"\n✅ Clean reports generated!")
    print(f"📊 Clean dataset summary:")
    print(f"   Total videos: {len(all_videos):,}")
    print(f"   Unique creators: {len(creators):,}")
    print(f"   Unique hashtags: {len(hashtag_counter):,}")
    print(f"   Search queries: {len(query_stats):,}")
    print(f"   Average engagement: {sum(v['engagement_rate'] for v in all_videos) / len(all_videos):.2f}%")

if __name__ == "__main__":
    main()