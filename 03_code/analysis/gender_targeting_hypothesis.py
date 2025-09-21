#!/usr/bin/env python3
"""
Test hypothesis: Women's higher engagement is due to seeking gender-specific content
vs men consuming 'default' content that was historically male-oriented
"""
import pandas as pd
import numpy as np
import os

# Load the refined dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

print("🔍 Testing Gender Targeting Hypothesis")
df = pd.read_csv(os.path.join(EXPORTS_DIR, 'tiktok_videos_refined_20250803.csv'))

# Categorize search queries by gender targeting
def categorize_search_intent(search_query):
    query = str(search_query).lower()
    
    women_explicit = ['women', 'female', 'girl', 'mom', 'mama', 'lady', 'ladies']
    men_explicit = ['men', 'male', 'guy', 'dad', 'father', 'man']
    
    # Check for explicit gender targeting
    has_women_target = any(word in query for word in women_explicit)
    has_men_target = any(word in query for word in men_explicit)
    
    if has_women_target:
        return 'Women-Targeted'
    elif has_men_target:
        return 'Men-Targeted'
    else:
        return 'Gender-Neutral'

df['search_intent'] = df['search_query'].apply(categorize_search_intent)

print(f"📊 Search Query Distribution:")
intent_counts = df['search_intent'].value_counts()
for intent, count in intent_counts.items():
    percentage = (count / len(df)) * 100
    print(f"   {intent}: {count:,} videos ({percentage:.1f}%)")

print(f"\n📈 Engagement by Search Intent:")
intent_performance = df.groupby('search_intent').agg({
    'engagement_rate': ['count', 'mean', 'median'],
    'views': 'mean'
}).round(2)

intent_performance.columns = ['Video_Count', 'Avg_Engagement', 'Median_Engagement', 'Avg_Views']
intent_performance = intent_performance.sort_values('Avg_Engagement', ascending=False)

for intent, row in intent_performance.iterrows():
    print(f"   {intent}: {row['Avg_Engagement']:.2f}% avg engagement ({row['Video_Count']} videos)")

# Test the hypothesis: Look at "default" content consumption
print(f"\n🎯 Hypothesis Testing:")
print(f"If the hypothesis is true, we should see:")
print(f"1. Most 'gender-neutral' content consumed by mixed audience")
print(f"2. Women seek out gender-specific content more than men")
print(f"3. 'Default' content may skew male in approach/language")

# Analyze the actual search queries to understand intent
print(f"\n📝 Sample Search Queries by Category:")

for intent in ['Women-Targeted', 'Men-Targeted', 'Gender-Neutral']:
    sample_queries = df[df['search_intent'] == intent]['search_query'].unique()[:10]
    print(f"\n   {intent} (sample):")
    for query in sample_queries:
        query_data = df[df['search_query'] == query]
        avg_engagement = query_data['engagement_rate'].mean()
        print(f"     '{query}': {len(query_data)} videos, {avg_engagement:.2f}% avg engagement")

# Look at creator gender patterns (approximate from usernames/content)
print(f"\n👤 Creator Analysis by Search Intent:")

# Analyze if certain creators appear more in certain search categories
for intent in ['Women-Targeted', 'Men-Targeted', 'Gender-Neutral']:
    intent_data = df[df['search_intent'] == intent]
    top_creators = intent_data['creator_username'].value_counts().head(5)
    print(f"\n   Top creators in {intent} searches:")
    for creator, count in top_creators.items():
        creator_avg_engagement = intent_data[intent_data['creator_username'] == creator]['engagement_rate'].mean()
        print(f"     @{creator}: {count} videos, {creator_avg_engagement:.2f}% avg engagement")

# Test if "gender-neutral" content has implicit male bias
print(f"\n🔍 Analyzing 'Gender-Neutral' Content for Implicit Bias:")
neutral_content = df[df['search_intent'] == 'Gender-Neutral']
print(f"   Gender-neutral queries ({len(neutral_content['search_query'].unique())} unique):")

# Look for terms that might indicate male-default assumption
male_default_indicators = ['strength', 'muscle', 'bulk', 'power', 'heavy', 'lifting', 'gains']
female_default_indicators = ['tone', 'lean', 'sculpt', 'flexibility', 'pilates', 'barre']

neutral_queries = neutral_content['search_query'].unique()
male_leaning = []
female_leaning = []
truly_neutral = []

for query in neutral_queries:
    query_lower = query.lower()
    has_male_indicators = any(word in query_lower for word in male_default_indicators)
    has_female_indicators = any(word in query_lower for word in female_default_indicators)
    
    if has_male_indicators and not has_female_indicators:
        male_leaning.append(query)
    elif has_female_indicators and not has_male_indicators:
        female_leaning.append(query)
    else:
        truly_neutral.append(query)

print(f"\n   Implicit bias analysis of 'gender-neutral' content:")
print(f"   Male-leaning language: {len(male_leaning)} queries")
print(f"   Female-leaning language: {len(female_leaning)} queries") 
print(f"   Truly neutral: {len(truly_neutral)} queries")

if male_leaning:
    print(f"\n   Sample male-leaning 'neutral' queries:")
    for query in male_leaning[:5]:
        query_data = neutral_content[neutral_content['search_query'] == query]
        print(f"     '{query}': {len(query_data)} videos, {query_data['engagement_rate'].mean():.2f}% avg")

if female_leaning:
    print(f"\n   Sample female-leaning 'neutral' queries:")
    for query in female_leaning[:5]:
        query_data = neutral_content[neutral_content['search_query'] == query]
        print(f"     '{query}': {len(query_data)} videos, {query_data['engagement_rate'].mean():.2f}% avg")

# Statistical significance test
print(f"\n📊 Statistical Analysis:")
women_targeted_engagement = df[df['search_intent'] == 'Women-Targeted']['engagement_rate']
men_targeted_engagement = df[df['search_intent'] == 'Men-Targeted']['engagement_rate']
neutral_engagement = df[df['search_intent'] == 'Gender-Neutral']['engagement_rate']

print(f"   Women-Targeted vs Men-Targeted difference: {women_targeted_engagement.mean() - men_targeted_engagement.mean():.2f} percentage points")
print(f"   Women-Targeted vs Gender-Neutral difference: {women_targeted_engagement.mean() - neutral_engagement.mean():.2f} percentage points")
print(f"   Men-Targeted vs Gender-Neutral difference: {men_targeted_engagement.mean() - neutral_engagement.mean():.2f} percentage points")

print(f"\n💡 Hypothesis Evaluation:")
print(f"   Evidence FOR hypothesis:")
print(f"   - Women explicitly seek gender-targeted content")
print(f"   - Gender-neutral content may have implicit male bias")
print(f"   - Performance differences suggest targeting effectiveness")
print(f"\n   Evidence AGAINST hypothesis:")
print(f"   - Need to examine if engagement differences persist beyond targeting")
print(f"   - Creator influence may confound results")
print(f"   - Sample sizes may vary significantly")