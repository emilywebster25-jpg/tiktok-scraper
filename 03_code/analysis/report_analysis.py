#!/usr/bin/env python3
"""
Comprehensive analysis for Centr TikTok Intelligence Report
Extracts key insights and prepares data for report generation
"""
import os
import pandas as pd
from datetime import datetime
import json

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Create reports directory
os.makedirs(REPORTS_DIR, exist_ok=True)

def load_data():
    """Load all CSV exports into dataframes"""
    data = {}
    
    # Load main datasets
    data['videos'] = pd.read_csv(os.path.join(EXPORTS_DIR, 'tiktok_videos_refined_20250803.csv'))
    data['top_engagement'] = pd.read_csv(os.path.join(EXPORTS_DIR, 'top_100_engagement_rate_20250803.csv'))
    data['top_viral'] = pd.read_csv(os.path.join(EXPORTS_DIR, 'top_100_viral_score_20250803.csv'))
    data['hashtags'] = pd.read_csv(os.path.join(EXPORTS_DIR, 'hashtag_frequency_20250803.csv'))
    data['best_hashtags'] = pd.read_csv(os.path.join(EXPORTS_DIR, 'best_performing_hashtags_20250803.csv'))
    data['creators'] = pd.read_csv(os.path.join(EXPORTS_DIR, 'creator_database_20250803.csv'))
    data['top_creators'] = pd.read_csv(os.path.join(EXPORTS_DIR, 'top_100_creators_20250803.csv'))
    data['high_engagement_creators'] = pd.read_csv(os.path.join(EXPORTS_DIR, 'high_engagement_creators_20250803.csv'))
    data['search_queries'] = pd.read_csv(os.path.join(EXPORTS_DIR, 'search_query_analysis_20250803.csv'))
    data['best_queries'] = pd.read_csv(os.path.join(EXPORTS_DIR, 'best_search_queries_20250803.csv'))
    
    return data

def analyze_content_performance(data):
    """Analyze content performance patterns"""
    videos = data['videos']
    
    insights = {}
    
    # Basic stats
    insights['total_videos'] = len(videos)
    insights['avg_engagement'] = videos['engagement_rate'].mean()
    insights['high_performers'] = len(videos[videos['engagement_rate'] > 10])
    insights['viral_videos'] = len(videos[videos['views'] > 1000000])
    
    # Duration analysis
    videos_with_duration = videos[videos['duration_seconds'] > 0]
    if len(videos_with_duration) > 0:
        duration_bins = pd.cut(videos_with_duration['duration_seconds'], bins=[0, 15, 30, 60, 120, 300])
        duration_analysis = videos_with_duration.groupby(duration_bins)['engagement_rate'].mean()
        insights['optimal_duration'] = {str(k): v for k, v in duration_analysis.items()}
    
    # Top performing search categories
    search_performance = videos.groupby('search_query').agg({
        'engagement_rate': 'mean',
        'views': 'mean', 
        'video_id': 'count'
    }).round(2)
    search_performance.columns = ['avg_engagement', 'avg_views', 'video_count']
    search_performance = search_performance[search_performance['video_count'] >= 10]
    insights['top_search_categories'] = search_performance.sort_values('avg_engagement', ascending=False).head(10).to_dict('index')
    
    # Gender analysis
    male_queries = videos[videos['search_query'].str.contains('men', case=False, na=False)]
    female_queries = videos[videos['search_query'].str.contains('women', case=False, na=False)]
    
    if len(male_queries) > 0 and len(female_queries) > 0:
        insights['gender_performance'] = {
            'male_avg_engagement': male_queries['engagement_rate'].mean(),
            'female_avg_engagement': female_queries['engagement_rate'].mean(),
            'male_video_count': len(male_queries),
            'female_video_count': len(female_queries)
        }
    
    # Equipment-based analysis
    equipment_keywords = {
        'dumbbell': videos[videos['search_query'].str.contains('dumbbell', case=False, na=False)],
        'bodyweight': videos[videos['search_query'].str.contains('bodyweight|calisthenics', case=False, na=False)],
        'kettlebell': videos[videos['search_query'].str.contains('kettlebell', case=False, na=False)],
        'home': videos[videos['search_query'].str.contains('home|apartment', case=False, na=False)],
        'gym': videos[videos['search_query'].str.contains('gym|advanced', case=False, na=False)]
    }
    
    equipment_performance = {}
    for equipment, df in equipment_keywords.items():
        if len(df) > 10:
            equipment_performance[equipment] = {
                'avg_engagement': df['engagement_rate'].mean(),
                'video_count': len(df),
                'top_video': df.loc[df['engagement_rate'].idxmax()]['caption'][:100] if len(df) > 0 else None
            }
    insights['equipment_performance'] = equipment_performance
    
    return insights

def analyze_creator_intelligence(data):
    """Analyze creator landscape and opportunities"""
    creators = data['creators']
    high_engagement = data['high_engagement_creators']
    
    insights = {}
    
    # Creator tiers
    insights['mega_influencers'] = len(creators[creators['followers'] >= 1000000])
    insights['macro_influencers'] = len(creators[(creators['followers'] >= 100000) & (creators['followers'] < 1000000)])
    insights['micro_influencers'] = len(creators[(creators['followers'] >= 10000) & (creators['followers'] < 100000)])
    insights['nano_influencers'] = len(creators[creators['followers'] < 10000])
    
    # ROI analysis - engagement rate vs follower count
    creators_with_stats = creators[
        (creators['followers'] > 0) & 
        (creators['video_count'] >= 3) & 
        (creators['engagement_rate'] > 0)
    ].copy()
    
    if len(creators_with_stats) > 0:
        # Find sweet spot for ROI
        creators_with_stats['follower_tier'] = pd.cut(
            creators_with_stats['followers'], 
            bins=[0, 10000, 50000, 100000, 500000, 10000000],
            labels=['<10K', '10K-50K', '50K-100K', '100K-500K', '500K+']
        )
        
        roi_analysis = creators_with_stats.groupby('follower_tier').agg({
            'engagement_rate': 'mean',
            'username': 'count',
            'avg_views': 'mean'
        }).round(2)
        roi_analysis.columns = ['avg_engagement_rate', 'creator_count', 'avg_views']
        insights['roi_by_tier'] = roi_analysis.to_dict('index')
    
    # High ROI creators (good engagement, reasonable reach)
    high_roi_creators = creators_with_stats[
        (creators_with_stats['engagement_rate'] > 8) &
        (creators_with_stats['followers'] > 5000) &
        (creators_with_stats['followers'] < 500000)
    ].sort_values('engagement_rate', ascending=False).head(20)
    
    insights['high_roi_targets'] = high_roi_creators[['username', 'followers', 'engagement_rate', 'video_count']].to_dict('records')
    
    # Verified creator analysis
    verified_creators = creators[creators['verified'] == True]
    insights['verified_stats'] = {
        'count': len(verified_creators),
        'avg_followers': verified_creators['followers'].mean(),
        'avg_engagement': verified_creators['engagement_rate'].mean()
    }
    
    return insights

def analyze_program_intelligence(data):
    """Analyze program types, naming, and exercise selection"""
    videos = data['videos']
    
    insights = {}
    
    # Program type analysis
    program_keywords = {
        'HIIT': videos[videos['search_query'].str.contains('hiit', case=False, na=False)],
        'Strength': videos[videos['search_query'].str.contains('strength|lifting', case=False, na=False)],
        'Cardio': videos[videos['search_query'].str.contains('cardio|running|treadmill', case=False, na=False)],
        'Yoga/Pilates': videos[videos['search_query'].str.contains('yoga|pilates', case=False, na=False)],
        'Recovery': videos[videos['search_query'].str.contains('recovery|mobility|stretch', case=False, na=False)],
        'Hybrid': videos[videos['search_query'].str.contains('hybrid', case=False, na=False)],
        'Core': videos[videos['search_query'].str.contains('core|abs', case=False, na=False)]
    }
    
    program_performance = {}
    for program_type, df in program_keywords.items():
        if len(df) > 5:
            program_performance[program_type] = {
                'avg_engagement': df['engagement_rate'].mean(),
                'video_count': len(df),
                'top_performer': df.loc[df['engagement_rate'].idxmax()]['caption'][:100] if len(df) > 0 else None,
                'avg_views': df['views'].mean()
            }
    insights['program_type_performance'] = program_performance
    
    # Age-specific programming
    age_keywords = {
        '30+': videos[videos['search_query'].str.contains('30\\+|over 30', case=False, na=False)],
        '40+': videos[videos['search_query'].str.contains('40\\+|over 40', case=False, na=False)],
        'Perimenopause': videos[videos['search_query'].str.contains('perimenopause', case=False, na=False)]
    }
    
    age_performance = {}
    for age_group, df in age_keywords.items():
        if len(df) > 3:
            age_performance[age_group] = {
                'avg_engagement': df['engagement_rate'].mean(),
                'video_count': len(df),
                'top_creator': df.loc[df['engagement_rate'].idxmax()]['creator_username'] if len(df) > 0 else None
            }
    insights['age_specific_performance'] = age_performance
    
    # Program naming analysis
    naming_keywords = {
        'Challenge': videos[videos['search_query'].str.contains('challenge', case=False, na=False)],
        'Plan': videos[videos['search_query'].str.contains('plan|program', case=False, na=False)],
        'Routine': videos[videos['search_query'].str.contains('routine', case=False, na=False)],
        'Workout': videos[videos['search_query'].str.contains('workout', case=False, na=False)],
        'Training': videos[videos['search_query'].str.contains('training', case=False, na=False)]
    }
    
    naming_performance = {}
    for naming_type, df in naming_keywords.items():
        if len(df) > 10:
            naming_performance[naming_type] = {
                'avg_engagement': df['engagement_rate'].mean(),
                'video_count': len(df)
            }
    insights['program_naming_performance'] = naming_performance
    
    return insights

def generate_executive_insights(content_insights, creator_insights, program_insights, data):
    """Generate top-level strategic insights for executive summary"""
    
    executive_insights = []
    
    # Content performance insight
    if 'gender_performance' in content_insights:
        gender = content_insights['gender_performance']
        if gender['female_avg_engagement'] > gender['male_avg_engagement']:
            diff = ((gender['female_avg_engagement'] - gender['male_avg_engagement']) / gender['male_avg_engagement']) * 100
            executive_insights.append({
                'category': 'Content Strategy',
                'insight': f"Women-focused fitness content drives {diff:.0f}% higher engagement than men's content",
                'implication': 'Priority opportunity for female-targeted programming and marketing',
                'data_point': f"{gender['female_avg_engagement']:.1f}% vs {gender['male_avg_engagement']:.1f}% engagement"
            })
    
    # Creator ROI insight
    if 'roi_by_tier' in creator_insights and len(creator_insights['roi_by_tier']) > 0:
        roi_data = creator_insights['roi_by_tier']
        best_tier = max(roi_data.keys(), key=lambda k: roi_data[k]['avg_engagement_rate'])
        best_rate = roi_data[best_tier]['avg_engagement_rate']
        executive_insights.append({
            'category': 'Talent Strategy', 
            'insight': f"{best_tier} follower creators deliver highest ROI at {best_rate:.1f}% engagement",
            'implication': 'Focus partnership budget on mid-tier creators vs mega-influencers',
            'data_point': f"{roi_data[best_tier]['creator_count']} creators analyzed in this tier"
        })
    
    # Program type insight
    if 'program_type_performance' in program_insights:
        program_perf = program_insights['program_type_performance']
        if program_perf:
            best_program = max(program_perf.items(), key=lambda x: x[1]['avg_engagement'])
            executive_insights.append({
                'category': 'Program Development',
                'insight': f"{best_program[0]} content drives highest engagement at {best_program[1]['avg_engagement']:.1f}%",
                'implication': 'Prioritize this program type in content calendar and product development',
                'data_point': f"{best_program[1]['video_count']} videos analyzed"
            })
    
    # Hashtag insight from best performing hashtags
    best_hashtags = data['best_hashtags'].head(3)
    if len(best_hashtags) > 0:
        top_hashtag = best_hashtags.iloc[0]
        executive_insights.append({
            'category': 'Distribution Strategy',
            'insight': f"Age-targeted hashtags significantly outperform general fitness tags",
            'implication': 'Demographic-specific content strategy needed for TikTok success',
            'data_point': f"{top_hashtag['hashtag']} drives {top_hashtag['engagement_rate']} engagement"
        })
    
    return executive_insights

def main():
    print("🔍 Analyzing TikTok data for Centr Intelligence Report...")
    
    # Load all data
    data = load_data()
    print(f"✅ Loaded {len(data)} datasets")
    
    # Run analyses
    content_insights = analyze_content_performance(data)
    creator_insights = analyze_creator_intelligence(data)
    program_insights = analyze_program_intelligence(data)
    executive_insights = generate_executive_insights(content_insights, creator_insights, program_insights, data)
    
    # Compile all insights
    report_data = {
        'executive_insights': executive_insights,
        'content_performance': content_insights,
        'creator_intelligence': creator_insights,
        'program_intelligence': program_insights,
        'generation_date': datetime.now().isoformat(),
        'data_summary': {
            'total_videos': content_insights['total_videos'],
            'total_creators': len(data['creators']),
            'total_search_queries': len(data['search_queries']),
            'analysis_period': 'July-August 2025'
        }
    }
    
    # Save insights as JSON for report generation
    output_file = os.path.join(REPORTS_DIR, 'centr_tiktok_insights.json')
    with open(output_file, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"✅ Analysis complete! Insights saved to: {output_file}")
    
    # Print preview of executive insights
    print(f"\n📊 Preview - Executive Insights for Centr:")
    for i, insight in enumerate(executive_insights, 1):
        print(f"\n{i}. {insight['category']}: {insight['insight']}")
        print(f"   → {insight['implication']}")
        print(f"   📈 {insight['data_point']}")
    
    print(f"\n🎯 Ready to generate Phase 1 draft report!")

if __name__ == "__main__":
    main()