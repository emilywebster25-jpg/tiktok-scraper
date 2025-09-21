#!/usr/bin/env python3
"""
Investigate the 105 "failed" videos with <1% engagement
This shouldn't exist if Apify scraped "top" videos as claimed
"""
import pandas as pd
import numpy as np
import os

# Load the refined dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

print("🔍 Investigating 'Failed' Content (<1% engagement)...")
df = pd.read_csv(os.path.join(EXPORTS_DIR, 'tiktok_videos_refined_20250803.csv'))

# Get the failed content
failed_content = df[df['engagement_rate'] < 1].copy()
print(f"📉 Found {len(failed_content)} videos with <1% engagement ({len(failed_content)/len(df)*100:.1f}% of total)")

print(f"\n📊 Basic Statistics of Failed Content:")
print(f"   Engagement Range: {failed_content['engagement_rate'].min():.3f}% - {failed_content['engagement_rate'].max():.3f}%")
print(f"   Average Views: {failed_content['views'].mean():,.0f}")
print(f"   Median Views: {failed_content['views'].median():,.0f}")
print(f"   Views Range: {failed_content['views'].min():,} - {failed_content['views'].max():,}")

# Look at search queries for failed content
print(f"\n🔎 Search Queries for Failed Content:")
failed_queries = failed_content['search_query'].value_counts()
print(f"   Top 10 search queries producing 'failed' content:")
for query, count in failed_queries.head(10).items():
    pct = (count / len(failed_content)) * 100
    print(f"   '{query}': {count} videos ({pct:.1f}%)")

# Compare to successful content from same queries
print(f"\n🔄 Comparing Failed vs Successful Content from Same Queries:")
for query in failed_queries.head(5).index:
    query_videos = df[df['search_query'] == query]
    failed_from_query = query_videos[query_videos['engagement_rate'] < 1]
    success_from_query = query_videos[query_videos['engagement_rate'] >= 1]
    
    print(f"\n   Query: '{query}'")
    print(f"   Total videos: {len(query_videos)}")
    print(f"   Failed (<1%): {len(failed_from_query)} ({len(failed_from_query)/len(query_videos)*100:.1f}%)")
    print(f"   Successful (≥1%): {len(success_from_query)} ({len(success_from_query)/len(query_videos)*100:.1f}%)")
    if len(success_from_query) > 0:
        print(f"   Successful avg engagement: {success_from_query['engagement_rate'].mean():.2f}%")

# Look at creators of failed content
print(f"\n👤 Creators with Failed Content:")
failed_creators = failed_content['creator_username'].value_counts()
print(f"   Creators with multiple failed videos:")
for creator, count in failed_creators.head(10).items():
    if count > 1:
        creator_videos = df[df['creator_username'] == creator]
        print(f"   @{creator}: {count} failed videos out of {len(creator_videos)} total")

# Look at timing patterns
print(f"\n⏰ When Was Failed Content Created?")
try:
    failed_content['created_date'] = pd.to_datetime(failed_content['create_time'])
    failed_content['created_month'] = failed_content['created_date'].dt.to_period('M')
    monthly_fails = failed_content['created_month'].value_counts().sort_index()
    print(f"   Failed content by month:")
    for month, count in monthly_fails.items():
        print(f"   {month}: {count} videos")
except Exception as e:
    print(f"   Could not analyze timing: {e}")

# Look at engagement components
print(f"\n💫 Engagement Breakdown for Failed Content:")
print(f"   Average Likes: {failed_content['likes'].mean():.0f}")
print(f"   Average Comments: {failed_content['comments'].mean():.0f}")
print(f"   Average Shares: {failed_content['shares'].mean():.0f}")
print(f"   Videos with ZERO likes: {len(failed_content[failed_content['likes'] == 0])}")
print(f"   Videos with ZERO comments: {len(failed_content[failed_content['comments'] == 0])}")
print(f"   Videos with ZERO shares: {len(failed_content[failed_content['shares'] == 0])}")

# Check if these are genuinely "failed" or data issues
print(f"\n🔍 Potential Data Quality Issues:")
zero_everything = failed_content[
    (failed_content['likes'] == 0) & 
    (failed_content['comments'] == 0) & 
    (failed_content['shares'] == 0)
]
print(f"   Videos with zero likes, comments, AND shares: {len(zero_everything)}")

high_views_low_engagement = failed_content[failed_content['views'] > 50000]
print(f"   Failed videos with >50K views (suspicious): {len(high_views_low_engagement)}")
if len(high_views_low_engagement) > 0:
    print(f"   Examples:")
    for idx, row in high_views_low_engagement.head(5).iterrows():
        print(f"     @{row['creator_username']}: {row['views']:,} views, {row['engagement_rate']:.3f}% engagement")

# Sample the actual failed content to understand patterns
print(f"\n📝 Sample Failed Content Analysis:")
print(f"   Random sample of 10 failed videos:")
sample_failed = failed_content.sample(min(10, len(failed_content)))
for idx, row in sample_failed.iterrows():
    caption_preview = row['caption'][:60] + "..." if len(str(row['caption'])) > 60 else row['caption']
    print(f"   @{row['creator_username']} | {row['views']:,} views | {row['engagement_rate']:.3f}% | {caption_preview}")

print(f"\n🤔 Key Questions:")
print(f"   1. Why would Apify's 'top content' scraper capture videos with <1% engagement?")
print(f"   2. Are these legitimate low-performers or data collection errors?")
print(f"   3. Do certain search queries consistently produce more 'failed' content?")
print(f"   4. Are these older videos that have declined in relevance?")