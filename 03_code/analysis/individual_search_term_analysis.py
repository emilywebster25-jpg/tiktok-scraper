#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_search_term(search_term, df):
    """
    Analyze a single search term and return detailed statistics
    """
    # Filter data for this search term
    term_data = df[df['search_query'] == search_term].copy()
    
    if len(term_data) == 0:
        return None
    
    # Calculate basic stats
    total_videos = len(term_data)
    avg_engagement = term_data['engagement_rate'].mean()
    median_engagement = term_data['engagement_rate'].median()
    avg_views = term_data['views'].mean()
    median_views = term_data['views'].median()
    
    # Performance tiers
    high_performers = term_data[term_data['engagement_rate'] > 10]
    good_performers = term_data[(term_data['engagement_rate'] > 6) & (term_data['engagement_rate'] <= 10)]
    average_performers = term_data[(term_data['engagement_rate'] > 3) & (term_data['engagement_rate'] <= 6)]
    low_performers = term_data[term_data['engagement_rate'] <= 3]
    
    # Success rates
    high_success_rate = len(high_performers) / total_videos * 100
    good_success_rate = len(good_performers) / total_videos * 100
    
    # Top performing video
    top_video = term_data.loc[term_data['engagement_rate'].idxmax()]
    
    # Creator diversity
    unique_creators = term_data['creator_username'].nunique()
    creator_diversity = unique_creators / total_videos
    
    # Date range
    term_data['create_time'] = pd.to_datetime(term_data['create_time'])
    date_range = (term_data['create_time'].min().strftime('%Y-%m-%d'), 
                  term_data['create_time'].max().strftime('%Y-%m-%d'))
    
    return {
        'search_term': search_term,
        'total_videos': total_videos,
        'avg_engagement': round(avg_engagement, 2),
        'median_engagement': round(median_engagement, 2),
        'avg_views': int(avg_views),
        'median_views': int(median_views),
        'high_performers_count': len(high_performers),
        'high_success_rate': round(high_success_rate, 1),
        'good_success_rate': round(good_success_rate, 1),
        'unique_creators': unique_creators,
        'creator_diversity': round(creator_diversity, 2),
        'date_range': date_range,
        'top_video': {
            'creator': top_video['creator_username'],
            'engagement_rate': round(top_video['engagement_rate'], 2),
            'view_count': int(top_video['views']),
            'video_id': top_video['video_id']
        },
        'performance_distribution': {
            'high_performers': len(high_performers),
            'good_performers': len(good_performers),
            'average_performers': len(average_performers),
            'low_performers': len(low_performers)
        }
    }

def main():
    # Load the refined dataset
    data_file = Path("exports/tiktok_videos_refined_20250803.csv")
    if not data_file.exists():
        print(f"Error: {data_file} not found")
        return
    
    df = pd.read_csv(data_file)
    
    # Get all unique search terms
    search_terms = sorted(df['search_query'].unique())
    
    print(f"Found {len(search_terms)} unique search terms")
    print("\nAvailable search terms:")
    for i, term in enumerate(search_terms, 1):
        print(f"{i:2d}. {term}")
    
    # Allow user to select a specific term
    print("\nEnter the number of the search term to analyze (or 'all' for all terms):")
    choice = input().strip()
    
    if choice.lower() == 'all':
        for term in search_terms:
            result = analyze_search_term(term, df)
            if result:
                print_analysis(result)
                print("-" * 80)
    else:
        try:
            term_index = int(choice) - 1
            if 0 <= term_index < len(search_terms):
                term = search_terms[term_index]
                result = analyze_search_term(term, df)
                if result:
                    print_analysis(result)
                else:
                    print(f"No data found for: {term}")
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")

def print_analysis(result):
    """
    Print a formatted analysis of a search term
    """
    print(f"\n📊 ANALYSIS: {result['search_term']}")
    print("=" * 60)
    
    # Sample size assessment
    if result['total_videos'] >= 100:
        confidence = "HIGH CONFIDENCE"
    elif result['total_videos'] >= 50:
        confidence = "RELIABLE"
    elif result['total_videos'] >= 20:
        confidence = "LIMITED DATA"
    else:
        confidence = "EXPLORATORY"
    
    print(f"📈 Sample Size: {result['total_videos']} videos ({confidence})")
    print(f"👥 Creator Diversity: {result['unique_creators']} creators (diversity: {result['creator_diversity']})")
    print(f"📅 Date Range: {result['date_range'][0]} to {result['date_range'][1]}")
    
    print(f"\n🎯 ENGAGEMENT PERFORMANCE:")
    print(f"   Average: {result['avg_engagement']}%")
    print(f"   Median:  {result['median_engagement']}%")
    print(f"   High performers (>10%): {result['high_performers_count']} videos ({result['high_success_rate']}%)")
    print(f"   Good performers (6-10%): {result['performance_distribution']['good_performers']} videos ({result['good_success_rate']}%)")
    
    print(f"\n👀 VIEW PERFORMANCE:")
    print(f"   Average views: {result['avg_views']:,}")
    print(f"   Median views:  {result['median_views']:,}")
    
    print(f"\n🏆 TOP PERFORMER:")
    print(f"   Creator: @{result['top_video']['creator']}")
    print(f"   Engagement: {result['top_video']['engagement_rate']}%")
    print(f"   Views: {result['top_video']['view_count']:,}")
    
    print(f"\n📊 PERFORMANCE BREAKDOWN:")
    total = result['total_videos']
    print(f"   High (>10%):     {result['performance_distribution']['high_performers']:3d} videos ({result['performance_distribution']['high_performers']/total*100:.1f}%)")
    print(f"   Good (6-10%):    {result['performance_distribution']['good_performers']:3d} videos ({result['performance_distribution']['good_performers']/total*100:.1f}%)")
    print(f"   Average (3-6%):  {result['performance_distribution']['average_performers']:3d} videos ({result['performance_distribution']['average_performers']/total*100:.1f}%)")
    print(f"   Low (≤3%):       {result['performance_distribution']['low_performers']:3d} videos ({result['performance_distribution']['low_performers']/total*100:.1f}%)")

if __name__ == "__main__":
    main()