# 📱 TikTok Data Scraper

**A Python tool for collecting TikTok videos and analyzing their content using Apify integration.**

## 📋 What It Is

This tool helps you collect and analyze TikTok videos at scale for research purposes. Instead of manually browsing TikTok and taking notes, it automatically downloads videos and extracts useful information like captions, engagement metrics, and audio transcriptions.

**Key Components:**
- 📥 **Automated video collection** using Apify's TikTok scraper
- 📊 **Metadata extraction** from video information and engagement data
- 🎵 **Content analysis** including speech-to-text from video audio
- 📁 **Organized storage** with structured file management
- 📈 **Data export** to CSV files for further analysis

## ⚙️ How It Works

### Basic Video Collection
1. **Set up search terms** for the type of content you want to collect
2. **Run the collection script** which uses Apify to download videos
3. **Let it process overnight** for large datasets
4. **Get organized folders** with videos, thumbnails, and metadata

### What It Actually Does
- **Downloads TikTok videos** and saves them locally with metadata
- **Extracts video information** like captions, hashtags, and engagement metrics
- **Organizes files automatically** into structured folders
- **Processes audio content** to extract speech-to-text when available
- **Exports data to CSV** for spreadsheet analysis

## 💡 Why I Made It

I needed to analyze fitness content trends on TikTok but manually browsing and taking notes was taking forever. I wanted to see patterns across hundreds of videos without spending weeks watching them individually.

**The Problem:** Manual TikTok research was time-consuming and inconsistent.

**My Approach:** Use Apify's professional scraping tools to automate the collection, then build Python scripts to organize and analyze the content.

## Quick Start Guide

### Option 1: Run with Existing Configuration
1. **Get an Apify API key** from their website
2. **Add your API key** to the configuration file
3. **Run the collection**: `python3 run_pipeline.py`
4. **Check the results** in organized folders

### Option 2: Customize Search Terms
1. **Edit the search configuration** with your keywords
2. **Set collection limits** (number of videos per search)
3. **Run targeted collection**: `python3 download_apify_data.py`
4. **Process the results** with analysis scripts

### Option 3: Analyze Existing Data
1. **Use the analysis scripts** in the `03_code/analysis/` folder
2. **Generate reports** from collected video data
3. **Export results** to CSV for further work

## Project Structure

```
tiktok-scraper/
├── 03_code/                     # Python scripts
│   ├── analysis/                # Data analysis scripts
│   ├── extraction/              # Video processing tools
│   └── utilities/               # Helper functions
├── run_pipeline.py              # Main execution script
└── README.md                    # Project documentation
```

## Key Features

- **📱 Large-Scale Collection**: Collect hundreds of videos automatically
- **🔍 Flexible Search**: Use any search terms or hashtags
- **📊 Rich Metadata**: Get engagement metrics, captions, and creator info
- **🎵 Audio Analysis**: Extract speech content from videos when available
- **📁 Auto-Organization**: Files organized by search term and date
- **📈 Data Export**: Results available in CSV format for analysis

## Real Results from This Project

**Collection Achievements:**
- **4,445 videos** collected across multiple search terms
- **276 different datasets** processed
- **Search terms included:** "dumbbell cardio", "bodyweight workout", "morning routine"

**Content Analysis Findings:**
- **8.8% of videos** contained speech content suitable for transcription
- **2.9% of videos** had clear, instructional fitness content
- **Audio transcription** more reliable than text overlay extraction

## Technical Details

**Tools Used:**
- **Python 3.9+** for all processing scripts
- **Apify API** for professional TikTok data collection
- **Requests library** for API communication
- **JSON processing** for metadata handling

**Data Collection Strategy:**
- Targeted search terms for specific content types
- Automated overnight collection for large datasets
- Error handling for failed downloads
- Quality validation for collected content

## Getting Help

This project is designed to work with Claude Code for:
- **Adding new search terms** to collection scripts
- **Understanding the analysis results** and data patterns
- **Modifying collection parameters** for different research needs
- **Interpreting the Python scripts** and data processing

---

*A practical tool for TikTok content research and trend analysis.*