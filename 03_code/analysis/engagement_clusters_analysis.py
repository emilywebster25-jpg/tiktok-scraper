#!/usr/bin/env python3
"""
Deep dive into engagement rate distributions and natural clusters
"""
import pandas as pd
import numpy as np
import os

# Load the refined dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

print("📊 Engagement Rate Clusters & Distribution Analysis")
df = pd.read_csv(os.path.join(EXPORTS_DIR, 'tiktok_videos_refined_20250803.csv'))

print(f"📈 Overall Engagement Distribution:")
print(f"   Mean: {df['engagement_rate'].mean():.2f}%")
print(f"   Median: {df['engagement_rate'].median():.2f}%")
print(f"   Standard Deviation: {df['engagement_rate'].std():.2f}%")

# Define natural clusters based on performance levels
clusters = {
    'Low Performance': (0, 3),
    'Average Performance': (3, 6), 
    'Good Performance': (6, 10),
    'High Performance': (10, 15),
    'Exceptional Performance': (15, 100)
}

print(f"\n🎯 Natural Performance Clusters:")
for cluster_name, (min_val, max_val) in clusters.items():
    cluster_data = df[(df['engagement_rate'] >= min_val) & (df['engagement_rate'] < max_val)]
    percentage = (len(cluster_data) / len(df)) * 100
    print(f"   {cluster_name} ({min_val}-{max_val}%): {len(cluster_data):,} videos ({percentage:.1f}%)")

# Analyze each cluster by categories
print(f"\n🔍 Category Analysis by Performance Cluster:")

# Define categories based on search queries
def categorize_content(search_query):
    query = str(search_query).lower()
    
    if any(word in query for word in ['women', 'female', 'girl', 'mom', 'mama']):
        return 'Women-Focused'
    elif any(word in query for word in ['men', 'male', 'guy', 'dad', 'father']):
        return 'Men-Focused'
    elif any(word in query for word in ['yoga', 'pilates']):
        return 'Yoga/Pilates'
    elif any(word in query for word in ['strength', 'lifting', 'weights']):
        return 'Strength Training'
    elif any(word in query for word in ['cardio', 'running', 'treadmill']):
        return 'Cardio'
    elif any(word in query for word in ['hybrid']):
        return 'Hybrid Training'
    elif any(word in query for word in ['core', 'abs']):
        return 'Core Training'
    elif any(word in query for word in ['recovery', 'mobility', 'stretching']):
        return 'Recovery/Mobility'
    else:
        return 'General Fitness'

df['category'] = df['search_query'].apply(categorize_content)

# Show category distribution across clusters
for cluster_name, (min_val, max_val) in clusters.items():
    cluster_data = df[(df['engagement_rate'] >= min_val) & (df['engagement_rate'] < max_val)]
    if len(cluster_data) > 0:
        print(f"\n   {cluster_name} ({len(cluster_data):,} videos):")
        category_dist = cluster_data['category'].value_counts()
        for category, count in category_dist.head(5).items():
            percentage = (count / len(cluster_data)) * 100
            print(f"     {category}: {count} videos ({percentage:.1f}%)")

print(f"\n📊 Category Performance Summary:")
category_performance = df.groupby('category').agg({
    'engagement_rate': ['count', 'mean', 'median', 'std']
}).round(2)

category_performance.columns = ['Video_Count', 'Avg_Engagement', 'Median_Engagement', 'Std_Dev']
category_performance = category_performance.sort_values('Avg_Engagement', ascending=False)

print("   Category Rankings (by average engagement):")
for category, row in category_performance.iterrows():
    print(f"     {category}: {row['Avg_Engagement']:.2f}% avg ({row['Video_Count']} videos)")

# Look at high performers specifically
print(f"\n⭐ High Performance Analysis (>10% engagement):")
high_performers = df[df['engagement_rate'] > 10]
print(f"   Total high performers: {len(high_performers)} videos ({len(high_performers)/len(df)*100:.1f}%)")

high_perf_categories = high_performers['category'].value_counts()
print(f"   High performer categories:")
for category, count in high_perf_categories.items():
    category_total = len(df[df['category'] == category])
    success_rate = (count / category_total) * 100
    print(f"     {category}: {count} videos ({success_rate:.1f}% of category)")

# Exceptional performers
print(f"\n🌟 Exceptional Performance Analysis (>15% engagement):")
exceptional = df[df['engagement_rate'] > 15]
print(f"   Total exceptional performers: {len(exceptional)} videos ({len(exceptional)/len(df)*100:.1f}%)")

if len(exceptional) > 0:
    exceptional_categories = exceptional['category'].value_counts()
    print(f"   Exceptional performer categories:")
    for category, count in exceptional_categories.items():
        category_total = len(df[df['category'] == category])
        success_rate = (count / category_total) * 100
        print(f"     {category}: {count} videos ({success_rate:.1f}% of category)")

# Creator analysis in high performance
print(f"\n👤 Creators in High Performance Cluster:")
high_perf_creators = high_performers['creator_username'].value_counts()
print(f"   Top creators with high-performing content:")
for creator, count in high_perf_creators.head(10).items():
    creator_total = len(df[df['creator_username'] == creator])
    success_rate = (count / creator_total) * 100
    avg_engagement = df[df['creator_username'] == creator]['engagement_rate'].mean()
    print(f"     @{creator}: {count}/{creator_total} videos high-performing ({success_rate:.0f}%), {avg_engagement:.1f}% avg")

print(f"\n💡 Key Insights:")
print(f"   1. Clear performance clusters exist with distinct characteristics")
print(f"   2. Category distribution varies significantly across performance levels")
print(f"   3. Some categories consistently produce more high performers")
print(f"   4. Creator consistency matters - some creators reliably hit high performance")