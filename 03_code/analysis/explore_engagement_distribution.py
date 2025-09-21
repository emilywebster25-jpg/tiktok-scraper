#!/usr/bin/env python3
"""
Explore engagement rate distributions to understand natural patterns
"""
import pandas as pd
import numpy as np
import os

# Load the refined dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

print("📊 Loading refined TikTok dataset...")
df = pd.read_csv(os.path.join(EXPORTS_DIR, 'tiktok_videos_refined_20250803.csv'))
print(f"✅ Loaded {len(df):,} videos")

# Basic engagement rate statistics
engagement_rates = df['engagement_rate'].dropna()
print(f"\n📈 Engagement Rate Distribution:")
print(f"   Count: {len(engagement_rates):,}")
print(f"   Mean: {engagement_rates.mean():.2f}%")
print(f"   Median: {engagement_rates.median():.2f}%")
print(f"   Standard Deviation: {engagement_rates.std():.2f}%")
print(f"   Min: {engagement_rates.min():.2f}%")
print(f"   Max: {engagement_rates.max():.2f}%")

# Percentiles
percentiles = [10, 25, 50, 75, 90, 95, 99]
print(f"\n📊 Percentiles:")
for p in percentiles:
    value = np.percentile(engagement_rates, p)
    print(f"   {p}th percentile: {value:.2f}%")

# Create bins to understand distribution
bins = [0, 1, 2, 3, 5, 7, 10, 15, 20, 30, 100]
bin_labels = ['0-1%', '1-2%', '2-3%', '3-5%', '5-7%', '7-10%', '10-15%', '15-20%', '20-30%', '30%+']
df['engagement_bin'] = pd.cut(df['engagement_rate'], bins=bins, labels=bin_labels, include_lowest=True)

print(f"\n🗂️  Engagement Rate Buckets:")
bin_counts = df['engagement_bin'].value_counts().sort_index()
total_videos = len(df)
for bin_name, count in bin_counts.items():
    percentage = (count / total_videos) * 100
    print(f"   {bin_name}: {count:,} videos ({percentage:.1f}%)")

# Look for natural clusters
print(f"\n🔍 Looking for natural clusters...")

# Videos with very low engagement (likely failed content)
low_engagement = df[df['engagement_rate'] < 1]
print(f"   Very low engagement (<1%): {len(low_engagement):,} videos ({len(low_engagement)/len(df)*100:.1f}%)")

# "Normal" performing content
normal_engagement = df[(df['engagement_rate'] >= 1) & (df['engagement_rate'] < 10)]
print(f"   Normal engagement (1-10%): {len(normal_engagement):,} videos ({len(normal_engagement)/len(df)*100:.1f}%)")

# High performing content
high_engagement = df[df['engagement_rate'] >= 10]
print(f"   High engagement (10%+): {len(high_engagement):,} videos ({len(high_engagement)/len(df)*100:.1f}%)")

# Super viral content
viral_engagement = df[df['engagement_rate'] >= 20]
print(f"   Viral engagement (20%+): {len(viral_engagement):,} videos ({len(viral_engagement)/len(df)*100:.1f}%)")

# Look at the top performers in detail
print(f"\n🌟 Top 20 Performers:")
top_20 = df.nlargest(20, 'engagement_rate')[['creator_username', 'engagement_rate', 'views', 'caption', 'search_query']]
for idx, row in top_20.iterrows():
    print(f"   {row['engagement_rate']:.1f}% - @{row['creator_username']} - {row['caption'][:50]}...")

# Check for outliers that might skew analysis
print(f"\n⚠️  Potential Outliers (>30% engagement):")
outliers = df[df['engagement_rate'] > 30]
if len(outliers) > 0:
    for idx, row in outliers.iterrows():
        print(f"   {row['engagement_rate']:.1f}% - @{row['creator_username']} - {row['views']:,} views - {row['caption'][:50]}...")
else:
    print("   No videos with >30% engagement")

# Views vs Engagement relationship
print(f"\n📈 Views vs Engagement Patterns:")
high_views = df[df['views'] > 1000000]  # 1M+ views
print(f"   Videos with 1M+ views: {len(high_views):,}")
if len(high_views) > 0:
    print(f"   Average engagement for viral videos: {high_views['engagement_rate'].mean():.2f}%")
    print(f"   Median engagement for viral videos: {high_views['engagement_rate'].median():.2f}%")

# Low views, high engagement (authentic engagement)
authentic_high = df[(df['views'] < 100000) & (df['engagement_rate'] > 15)]
print(f"   Low views (<100K) but high engagement (>15%): {len(authentic_high):,} videos")

print(f"\n💡 Initial Observations:")
print(f"   1. Distribution appears to be right-skewed (long tail of high performers)")
print(f"   2. Most content ({len(normal_engagement):,} videos) falls in 1-10% range")
print(f"   3. High performers (10%+) are {len(high_engagement)/len(df)*100:.1f}% of total - quite rare")
print(f"   4. Viral content (20%+) is extremely rare at {len(viral_engagement)/len(df)*100:.1f}%")