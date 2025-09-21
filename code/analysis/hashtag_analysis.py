#!/usr/bin/env python3
"""
Analyze hashtag usage patterns and effectiveness
"""
import os
import json
import csv
import re
from collections import Counter, defaultdict
from datetime import datetime

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APIFY_DIR = os.path.join(BASE_DIR, "apify_downloads")
OUTPUT_DIR = os.path.join(BASE_DIR, "exports")

def extract_hashtags(text):
    """Extract hashtags from text"""
    return [tag.lower() for tag in re.findall(r'#(\w+)', text)]

def main():
    print("🏷️  Analyzing hashtag patterns...")
    
    hashtag_counter = Counter()
    hashtag_stats = defaultdict(lambda: {'videos': 0, 'total_views': 0, 'total_engagement': 0})
    hashtag_combinations = Counter()
    modality_hashtags = defaultdict(Counter)
    
    # Define modality keywords
    modalities = {
        'strength': ['strength', 'lifting', 'weights', 'powerlifting', 'strongman'],
        'cardio': ['cardio', 'hiit', 'running', 'cycling', 'endurance'],
        'yoga': ['yoga', 'pilates', 'flexibility', 'stretch'],
        'crossfit': ['crossfit', 'wod', 'metcon', 'amrap'],
        'calisthenics': ['calisthenics', 'bodyweight', 'pullups', 'pushups'],
        'general': ['fitness', 'workout', 'exercise', 'gym', 'training']
    }
    
    all_videos_data = []
    
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
                    text = video_data.get('text', '')
                    hashtags = extract_hashtags(text)
                    
                    if hashtags:
                        # Count individual hashtags
                        for tag in hashtags:
                            hashtag_counter[tag] += 1
                            hashtag_stats[tag]['videos'] += 1
                            hashtag_stats[tag]['total_views'] += video_data.get('playCount', 0)
                            
                            engagement = (video_data.get('diggCount', 0) + 
                                        video_data.get('commentCount', 0) + 
                                        video_data.get('shareCount', 0))
                            hashtag_stats[tag]['total_engagement'] += engagement
                        
                        # Count hashtag combinations (pairs)
                        if len(hashtags) > 1:
                            for i in range(len(hashtags)):
                                for j in range(i+1, len(hashtags)):
                                    pair = tuple(sorted([hashtags[i], hashtags[j]]))
                                    hashtag_combinations[pair] += 1
                        
                        # Categorize by modality
                        video_modality = 'other'
                        text_lower = text.lower()
                        for modality, keywords in modalities.items():
                            if any(keyword in text_lower for keyword in keywords):
                                video_modality = modality
                                break
                        
                        for tag in hashtags:
                            modality_hashtags[video_modality][tag] += 1
                        
                        # Store for detailed analysis
                        all_videos_data.append({
                            'video_id': video_data.get('id', ''),
                            'hashtags': hashtags,
                            'hashtag_count': len(hashtags),
                            'views': video_data.get('playCount', 0),
                            'engagement': engagement,
                            'modality': video_modality
                        })
        
        except Exception as e:
            print(f"⚠️  Error processing {json_file}: {e}")
    
    # Calculate average stats for each hashtag
    for tag in hashtag_stats:
        stats = hashtag_stats[tag]
        stats['avg_views'] = stats['total_views'] / stats['videos'] if stats['videos'] > 0 else 0
        stats['avg_engagement'] = stats['total_engagement'] / stats['videos'] if stats['videos'] > 0 else 0
        stats['engagement_rate'] = (stats['total_engagement'] / stats['total_views'] * 100) if stats['total_views'] > 0 else 0
    
    # 1. Top 100 hashtags by frequency
    print("\n📊 Top Hashtags by Frequency")
    freq_file = os.path.join(OUTPUT_DIR, f'hashtag_frequency_{datetime.now().strftime("%Y%m%d")}.csv')
    
    with open(freq_file, 'w', newline='', encoding='utf-8') as csvfile:
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
    
    print(f"✅ Saved: {freq_file}")
    
    # 2. Top hashtag combinations
    print("\n🔗 Top Hashtag Combinations")
    combo_file = os.path.join(OUTPUT_DIR, f'hashtag_combinations_{datetime.now().strftime("%Y%m%d")}.csv')
    
    with open(combo_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['rank', 'hashtag_1', 'hashtag_2', 'count'])
        
        for i, ((tag1, tag2), count) in enumerate(hashtag_combinations.most_common(50), 1):
            writer.writerow([i, f"#{tag1}", f"#{tag2}", count])
    
    print(f"✅ Saved: {combo_file}")
    
    # 3. Hashtags by modality
    print("\n🏋️ Top Hashtags by Workout Type")
    modality_file = os.path.join(OUTPUT_DIR, f'hashtags_by_modality_{datetime.now().strftime("%Y%m%d")}.csv')
    
    with open(modality_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['modality', 'hashtag', 'count'])
        
        for modality in ['strength', 'cardio', 'yoga', 'crossfit', 'calisthenics', 'general', 'other']:
            if modality in modality_hashtags:
                for tag, count in modality_hashtags[modality].most_common(20):
                    writer.writerow([modality, f"#{tag}", count])
    
    print(f"✅ Saved: {modality_file}")
    
    # 4. Best performing hashtags (by engagement rate)
    print("\n⭐ Best Performing Hashtags")
    best_hashtags = sorted(
        [(tag, stats) for tag, stats in hashtag_stats.items() if stats['videos'] >= 10],
        key=lambda x: x[1]['engagement_rate'],
        reverse=True
    )[:50]
    
    best_file = os.path.join(OUTPUT_DIR, f'best_performing_hashtags_{datetime.now().strftime("%Y%m%d")}.csv')
    
    with open(best_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['rank', 'hashtag', 'videos', 'engagement_rate', 'avg_views', 'avg_engagement'])
        
        for i, (tag, stats) in enumerate(best_hashtags, 1):
            writer.writerow([
                i, f"#{tag}", stats['videos'],
                f"{stats['engagement_rate']:.2f}%",
                f"{stats['avg_views']:.0f}",
                f"{stats['avg_engagement']:.0f}"
            ])
    
    print(f"✅ Saved: {best_file}")
    
    # Print summary
    print("\n📈 Hashtag Summary:")
    print(f"   Total unique hashtags: {len(hashtag_counter):,}")
    print(f"   Total hashtag uses: {sum(hashtag_counter.values()):,}")
    print(f"   Average hashtags per video: {sum(v['hashtag_count'] for v in all_videos_data) / len(all_videos_data):.1f}")
    
    print("\n🏷️  Top 10 Most Used Hashtags:")
    for i, (tag, count) in enumerate(hashtag_counter.most_common(10), 1):
        print(f"   {i}. #{tag} ({count:,} uses)")
    
    print("\n💎 Top 5 Best Performing Hashtags (min 10 videos):")
    for i, (tag, stats) in enumerate(best_hashtags[:5], 1):
        print(f"   {i}. #{tag} ({stats['engagement_rate']:.1f}% engagement on {stats['videos']} videos)")

if __name__ == "__main__":
    main()