#!/usr/bin/env python3
"""
Temporal analysis: Split established vs emerging content to validate findings
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Load the refined dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

print("⏰ Temporal Content Analysis: Established vs Emerging")
df = pd.read_csv(os.path.join(EXPORTS_DIR, 'tiktok_videos_refined_20250803.csv'))

# Convert create_time to datetime
df['created_date'] = pd.to_datetime(df['create_time']).dt.tz_localize(None)  # Remove timezone info
now = datetime.now()
df['content_age_days'] = (now - df['created_date']).dt.days

# Define content categories
cutoff_date = now - timedelta(days=180)  # 6 months ago
established_content = df[df['created_date'] < cutoff_date].copy()
emerging_content = df[df['created_date'] >= cutoff_date].copy()

print(f"📊 Content Age Split:")
print(f"   Established content (>6 months): {len(established_content):,} videos")
print(f"   Emerging content (<6 months): {len(emerging_content):,} videos")
print(f"   Average age of established: {established_content['content_age_days'].mean():.0f} days")
print(f"   Average age of emerging: {emerging_content['content_age_days'].mean():.0f} days")

# Compare engagement patterns
print(f"\n📈 Engagement Patterns by Content Age:")
print(f"   Established content average engagement: {established_content['engagement_rate'].mean():.2f}%")
print(f"   Emerging content average engagement: {emerging_content['engagement_rate'].mean():.2f}%")
print(f"   Established content median engagement: {established_content['engagement_rate'].median():.2f}%")
print(f"   Emerging content median engagement: {emerging_content['engagement_rate'].median():.2f}%")

# Check our key claims with temporal awareness
print(f"\n🔍 Re-validating Key Claims with Temporal Control:")

# Claim 1: Women's content drives higher engagement
print(f"\n1. Gender Performance Gap (Temporal Analysis):")

def analyze_gender_performance(data, label):
    women_indicators = ['women', 'female', 'girl', 'mom', 'mama']
    men_indicators = ['men', 'male', 'guy', 'dad', 'father']
    
    women_content = data[data['search_query'].str.contains('|'.join(women_indicators), case=False, na=False)]
    men_content = data[data['search_query'].str.contains('|'.join(men_indicators), case=False, na=False)]
    
    print(f"   {label}:")
    print(f"     Women's content: {len(women_content)} videos, {women_content['engagement_rate'].mean():.2f}% avg engagement")
    print(f"     Men's content: {len(men_content)} videos, {men_content['engagement_rate'].mean():.2f}% avg engagement")
    
    if len(women_content) > 0 and len(men_content) > 0:
        diff = women_content['engagement_rate'].mean() - men_content['engagement_rate'].mean()
        print(f"     Difference: {diff:.2f} percentage points")

analyze_gender_performance(established_content, "Established Content")
analyze_gender_performance(emerging_content, "Emerging Content")

# Claim 2: Program type performance
print(f"\n2. Program Type Performance (Temporal Analysis):")

def analyze_program_types(data, label):
    program_keywords = {
        'yoga': ['yoga', 'pilates'],
        'strength': ['strength', 'lifting', 'weights'],
        'cardio': ['cardio', 'running', 'treadmill'],
        'hybrid': ['hybrid'],
        'core': ['core', 'abs']
    }
    
    print(f"   {label}:")
    for program, keywords in program_keywords.items():
        program_content = data[data['search_query'].str.contains('|'.join(keywords), case=False, na=False)]
        if len(program_content) > 0:
            print(f"     {program.title()}: {len(program_content)} videos, {program_content['engagement_rate'].mean():.2f}% avg")

analyze_program_types(established_content, "Established Content")
analyze_program_types(emerging_content, "Emerging Content")

# Look for emerging trends
print(f"\n🌊 Emerging Trends (Recent 6 months):")
recent_top_queries = emerging_content['search_query'].value_counts().head(10)
print(f"   Top 10 search queries in recent content:")
for query, count in recent_top_queries.items():
    query_data = emerging_content[emerging_content['search_query'] == query]
    avg_engagement = query_data['engagement_rate'].mean()
    print(f"     '{query}': {count} videos, {avg_engagement:.2f}% avg engagement")

# High-performing emerging content
print(f"\n⭐ High-Performing Emerging Content (>10% engagement, <6 months old):")
emerging_winners = emerging_content[emerging_content['engagement_rate'] > 10].copy()
if len(emerging_winners) > 0:
    print(f"   Found {len(emerging_winners)} high-performing recent videos:")
    top_emerging = emerging_winners.nlargest(10, 'engagement_rate')
    for idx, row in top_emerging.iterrows():
        caption_preview = str(row['caption'])[:50] + "..." if len(str(row['caption'])) > 50 else str(row['caption'])
        age_days = row['content_age_days']
        print(f"     {row['engagement_rate']:.1f}% - @{row['creator_username']} ({age_days} days old) - {caption_preview}")

# Creator consistency across time periods
print(f"\n👤 Creator Performance: Established vs Emerging:")
creators_in_both = set(established_content['creator_username']) & set(emerging_content['creator_username'])
print(f"   Creators with content in both periods: {len(creators_in_both)}")

consistent_performers = []
for creator in list(creators_in_both)[:10]:  # Sample first 10
    est_perf = established_content[established_content['creator_username'] == creator]['engagement_rate'].mean()
    emer_perf = emerging_content[emerging_content['creator_username'] == creator]['engagement_rate'].mean()
    est_count = len(established_content[established_content['creator_username'] == creator])
    emer_count = len(emerging_content[emerging_content['creator_username'] == creator])
    
    if est_count >= 2 and emer_count >= 2:  # At least 2 videos in each period
        consistent_performers.append({
            'creator': creator,
            'established_avg': est_perf,
            'emerging_avg': emer_perf,
            'difference': emer_perf - est_perf,
            'est_count': est_count,
            'emer_count': emer_count
        })

if consistent_performers:
    print(f"   Creator performance changes (sample):")
    for perf in consistent_performers:
        trend = "↗️" if perf['difference'] > 1 else "↘️" if perf['difference'] < -1 else "➡️"
        print(f"     @{perf['creator']}: {perf['established_avg']:.1f}% → {perf['emerging_avg']:.1f}% {trend}")

print(f"\n💡 Key Insights:")
print(f"   1. Temporal splits show different engagement patterns for established vs emerging content")
print(f"   2. Recent content needs time to accumulate engagement - not inherently 'failed'")
print(f"   3. Emerging trends may indicate future high-performers")
print(f"   4. Creator consistency analysis helps identify sustainable performers")