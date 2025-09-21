#!/usr/bin/env python3
"""
Analyze search query performance - which searches yielded the best content
"""
import os
import json
import csv
from collections import defaultdict
from datetime import datetime
import statistics

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APIFY_DIR = os.path.join(BASE_DIR, "apify_downloads")
OUTPUT_DIR = os.path.join(BASE_DIR, "exports")

def main():
    print("🔍 Analyzing search query performance...")
    
    query_stats = defaultdict(lambda: {
        'videos': [],
        'total_views': 0,
        'total_engagement': 0,
        'engagement_rates': [],
        'follower_counts': [],
        'video_durations': []
    })
    
    # Process all JSON files
    json_files = [f for f in os.listdir(APIFY_DIR) if f.endswith('.json') and f.startswith('tiktok_')]
    
    for json_file in sorted(json_files):
        # Extract search query
        search_query = json_file[7:]  # Remove 'tiktok_'
        search_query = '_'.join(search_query.split('_')[:-2])  # Remove timestamp
        search_query_display = search_query.replace('_', ' ')
        
        json_path = os.path.join(APIFY_DIR, json_file)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for video_data in data:
                    views = video_data.get('playCount', 0)
                    likes = video_data.get('diggCount', 0)
                    comments = video_data.get('commentCount', 0)
                    shares = video_data.get('shareCount', 0)
                    engagement = likes + comments + shares
                    
                    engagement_rate = (engagement / views * 100) if views > 0 else 0
                    
                    query_stats[search_query_display]['videos'].append({
                        'id': video_data.get('id', ''),
                        'caption': video_data.get('text', '')[:100],
                        'creator': video_data.get('authorMeta', {}).get('name', ''),
                        'views': views,
                        'engagement': engagement,
                        'engagement_rate': engagement_rate
                    })
                    
                    query_stats[search_query_display]['total_views'] += views
                    query_stats[search_query_display]['total_engagement'] += engagement
                    query_stats[search_query_display]['engagement_rates'].append(engagement_rate)
                    query_stats[search_query_display]['follower_counts'].append(
                        video_data.get('authorMeta', {}).get('fans', 0)
                    )
                    query_stats[search_query_display]['video_durations'].append(
                        video_data.get('videoMeta', {}).get('duration', 0)
                    )
        
        except Exception as e:
            print(f"⚠️  Error processing {json_file}: {e}")
    
    # Calculate summary stats for each query
    query_summary = []
    for query, stats in query_stats.items():
        video_count = len(stats['videos'])
        if video_count > 0:
            # Calculate averages and medians
            avg_views = stats['total_views'] / video_count
            avg_engagement = stats['total_engagement'] / video_count
            avg_engagement_rate = statistics.mean(stats['engagement_rates'])
            median_engagement_rate = statistics.median(stats['engagement_rates'])
            
            # Find best performing video
            best_video = max(stats['videos'], key=lambda x: x['engagement_rate'])
            
            # High performer count (>10% engagement)
            high_performers = len([v for v in stats['videos'] if v['engagement_rate'] > 10])
            
            # Average creator size
            avg_creator_followers = statistics.mean(stats['follower_counts']) if stats['follower_counts'] else 0
            
            # Average video duration
            avg_duration = statistics.mean(stats['video_durations']) if stats['video_durations'] else 0
            
            query_summary.append({
                'search_query': query,
                'video_count': video_count,
                'total_views': stats['total_views'],
                'total_engagement': stats['total_engagement'],
                'avg_views': avg_views,
                'avg_engagement': avg_engagement,
                'avg_engagement_rate': avg_engagement_rate,
                'median_engagement_rate': median_engagement_rate,
                'high_performers': high_performers,
                'high_performer_pct': (high_performers / video_count * 100),
                'avg_creator_followers': avg_creator_followers,
                'avg_video_duration': avg_duration,
                'best_video_creator': best_video['creator'],
                'best_video_engagement': best_video['engagement_rate'],
                'best_video_caption': best_video['caption']
            })
    
    # 1. Full search query analysis
    print("\n📊 Search Query Performance Analysis")
    full_file = os.path.join(OUTPUT_DIR, f'search_query_analysis_{datetime.now().strftime("%Y%m%d")}.csv')
    
    fieldnames = ['search_query', 'video_count', 'avg_views', 'avg_engagement_rate', 
                  'median_engagement_rate', 'high_performers', 'high_performer_pct',
                  'avg_creator_followers', 'avg_video_duration']
    
    with open(full_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for query in sorted(query_summary, key=lambda x: x['avg_engagement_rate'], reverse=True):
            writer.writerow({k: query[k] for k in fieldnames})
    
    print(f"✅ Saved: {full_file}")
    
    # 2. Best queries by engagement
    print("\n⭐ Best Search Queries by Engagement")
    best_queries = sorted(query_summary, key=lambda x: x['avg_engagement_rate'], reverse=True)[:30]
    
    best_file = os.path.join(OUTPUT_DIR, f'best_search_queries_{datetime.now().strftime("%Y%m%d")}.csv')
    
    best_fieldnames = ['rank', 'search_query', 'video_count', 'avg_engagement_rate', 
                       'high_performer_pct', 'best_video_creator', 'best_video_engagement', 
                       'best_video_caption']
    
    with open(best_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=best_fieldnames)
        writer.writeheader()
        for i, query in enumerate(best_queries, 1):
            row = {'rank': i}
            row.update({k: query[k] for k in best_fieldnames[1:]})
            writer.writerow(row)
    
    print(f"✅ Saved: {best_file}")
    
    # 3. Query category analysis
    print("\n🏷️  Query Category Performance")
    categories = {
        'equipment': ['dumbbell', 'kettlebell', 'barbell', 'resistance', 'cable'],
        'modality': ['strength', 'cardio', 'hiit', 'yoga', 'pilates', 'crossfit'],
        'demographic': ['men', 'women', '30+', '40+', 'perimenopause', 'beginner'],
        'location': ['home', 'gym', 'outdoor'],
        'program': ['program', 'plan', 'routine', 'split', 'workout']
    }
    
    category_stats = defaultdict(lambda: {'queries': [], 'total_videos': 0, 'total_engagement_rate': 0})
    
    for query in query_summary:
        query_lower = query['search_query'].lower()
        for category, keywords in categories.items():
            if any(keyword in query_lower for keyword in keywords):
                category_stats[category]['queries'].append(query['search_query'])
                category_stats[category]['total_videos'] += query['video_count']
                category_stats[category]['total_engagement_rate'] += query['avg_engagement_rate']
    
    category_file = os.path.join(OUTPUT_DIR, f'query_category_analysis_{datetime.now().strftime("%Y%m%d")}.csv')
    
    with open(category_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['category', 'query_count', 'total_videos', 'avg_engagement_rate', 'example_queries'])
        
        for category, stats in category_stats.items():
            if stats['queries']:
                avg_rate = stats['total_engagement_rate'] / len(stats['queries'])
                examples = ', '.join(stats['queries'][:3])
                writer.writerow([
                    category,
                    len(stats['queries']),
                    stats['total_videos'],
                    f"{avg_rate:.2f}%",
                    examples
                ])
    
    print(f"✅ Saved: {category_file}")
    
    # Print summary
    print("\n📈 Search Query Summary:")
    print(f"   Total search queries: {len(query_summary)}")
    print(f"   Average videos per query: {statistics.mean([q['video_count'] for q in query_summary]):.0f}")
    print(f"   Queries with 40+ videos: {len([q for q in query_summary if q['video_count'] >= 40])}")
    
    print("\n🌟 Top 5 Search Queries by Engagement:")
    for i, query in enumerate(best_queries[:5], 1):
        print(f"   {i}. '{query['search_query']}' - {query['avg_engagement_rate']:.1f}% avg engagement "
              f"({query['video_count']} videos)")
    
    print("\n📊 Category Performance:")
    for category, stats in category_stats.items():
        if stats['queries']:
            avg_rate = stats['total_engagement_rate'] / len(stats['queries'])
            print(f"   {category.capitalize()}: {avg_rate:.1f}% avg engagement across {len(stats['queries'])} queries")

if __name__ == "__main__":
    main()