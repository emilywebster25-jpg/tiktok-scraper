#!/usr/bin/env python3
"""
Analyze creators and export creator database with performance metrics
"""
import os
import json
import csv
from collections import defaultdict
from datetime import datetime

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APIFY_DIR = os.path.join(BASE_DIR, "apify_downloads")
OUTPUT_DIR = os.path.join(BASE_DIR, "exports")

def main():
    print("👥 Analyzing creators...")
    
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
    
    # Process all JSON files
    json_files = [f for f in os.listdir(APIFY_DIR) if f.endswith('.json') and f.startswith('tiktok_')]
    
    for json_file in sorted(json_files):
        search_query = json_file[7:]
        search_query = '_'.join(search_query.split('_')[:-2])
        
        json_path = os.path.join(APIFY_DIR, json_file)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for video_data in data:
                    author_meta = video_data.get('authorMeta', {})
                    username = author_meta.get('name', '')
                    
                    if username:
                        creator = creators[username]
                        
                        # Update creator info
                        creator['followers'] = author_meta.get('fans', 0)
                        creator['verified'] = author_meta.get('verified', False)
                        creator['bio'] = author_meta.get('signature', '')
                        creator['nickname'] = author_meta.get('nickName', '')
                        
                        # Add video stats
                        views = video_data.get('playCount', 0)
                        likes = video_data.get('diggCount', 0)
                        comments = video_data.get('commentCount', 0)
                        shares = video_data.get('shareCount', 0)
                        
                        creator['total_views'] += views
                        creator['total_likes'] += likes
                        creator['total_comments'] += comments
                        creator['total_shares'] += shares
                        
                        creator['videos'].append({
                            'id': video_data.get('id', ''),
                            'views': views,
                            'engagement': likes + comments + shares,
                            'caption': video_data.get('text', '')[:100],
                            'search_query': search_query
                        })
        
        except Exception as e:
            print(f"⚠️  Error processing {json_file}: {e}")
    
    # Calculate metrics for each creator
    creator_stats = []
    for username, data in creators.items():
        video_count = len(data['videos'])
        if video_count > 0:
            avg_views = data['total_views'] / video_count
            avg_engagement = (data['total_likes'] + data['total_comments'] + data['total_shares']) / video_count
            engagement_rate = ((data['total_likes'] + data['total_comments'] + data['total_shares']) / 
                             data['total_views'] * 100) if data['total_views'] > 0 else 0
            
            # Find most popular video
            best_video = max(data['videos'], key=lambda x: x['engagement']) if data['videos'] else None
            
            creator_stats.append({
                'username': username,
                'nickname': data['nickname'],
                'followers': data['followers'],
                'verified': data['verified'],
                'bio': data['bio'][:200],  # First 200 chars
                'video_count': video_count,
                'total_views': data['total_views'],
                'total_engagement': data['total_likes'] + data['total_comments'] + data['total_shares'],
                'avg_views': avg_views,
                'avg_engagement': avg_engagement,
                'engagement_rate': engagement_rate,
                'best_video_caption': best_video['caption'] if best_video else '',
                'best_video_views': best_video['views'] if best_video else 0,
                'search_queries': ', '.join(set(v['search_query'] for v in data['videos']))
            })
    
    # 1. All creators database
    print("\n📊 Full Creator Database")
    all_creators_file = os.path.join(OUTPUT_DIR, f'creator_database_{datetime.now().strftime("%Y%m%d")}.csv')
    
    fieldnames = ['username', 'nickname', 'followers', 'verified', 'video_count', 
                  'total_views', 'total_engagement', 'avg_views', 'avg_engagement', 
                  'engagement_rate', 'bio', 'search_queries']
    
    with open(all_creators_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for creator in sorted(creator_stats, key=lambda x: x['followers'], reverse=True):
            writer.writerow({k: creator[k] for k in fieldnames})
    
    print(f"✅ Saved: {all_creators_file}")
    
    # 2. Top 100 creators by followers
    print("\n👑 Top Creators by Followers")
    top_creators = sorted(creator_stats, key=lambda x: x['followers'], reverse=True)[:100]
    
    top_file = os.path.join(OUTPUT_DIR, f'top_100_creators_{datetime.now().strftime("%Y%m%d")}.csv')
    
    with open(top_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['rank'] + fieldnames)
        writer.writeheader()
        for i, creator in enumerate(top_creators, 1):
            row = {'rank': i}
            row.update({k: creator[k] for k in fieldnames})
            writer.writerow(row)
    
    print(f"✅ Saved: {top_file}")
    
    # 3. High engagement creators (min 5 videos)
    print("\n⭐ High Engagement Creators")
    high_engagement = sorted(
        [c for c in creator_stats if c['video_count'] >= 5],
        key=lambda x: x['engagement_rate'],
        reverse=True
    )[:50]
    
    engagement_file = os.path.join(OUTPUT_DIR, f'high_engagement_creators_{datetime.now().strftime("%Y%m%d")}.csv')
    
    fieldnames_engagement = ['rank', 'username', 'followers', 'video_count', 
                           'engagement_rate', 'avg_views', 'avg_engagement', 'best_video_caption']
    
    with open(engagement_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames_engagement)
        writer.writeheader()
        for i, creator in enumerate(high_engagement, 1):
            row = {'rank': i}
            row.update({k: creator[k] for k in fieldnames_engagement[1:]})
            writer.writerow(row)
    
    print(f"✅ Saved: {engagement_file}")
    
    # Print summary
    print("\n📈 Creator Summary:")
    print(f"   Total unique creators: {len(creators):,}")
    print(f"   Verified creators: {len([c for c in creator_stats if c['verified']]):,}")
    print(f"   Creators with 1M+ followers: {len([c for c in creator_stats if c['followers'] >= 1000000]):,}")
    print(f"   Creators with 100k+ followers: {len([c for c in creator_stats if c['followers'] >= 100000]):,}")
    
    print("\n👑 Top 5 Creators by Followers:")
    for i, creator in enumerate(top_creators[:5], 1):
        print(f"   {i}. @{creator['username']} ({creator['followers']:,} followers, "
              f"{creator['video_count']} videos)")
    
    print("\n⭐ Top 5 by Engagement Rate (min 5 videos):")
    for i, creator in enumerate(high_engagement[:5], 1):
        print(f"   {i}. @{creator['username']} ({creator['engagement_rate']:.1f}% engagement, "
              f"{creator['followers']:,} followers)")

if __name__ == "__main__":
    main()