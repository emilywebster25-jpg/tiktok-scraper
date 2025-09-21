# TikTok Dataset Analysis Plan

## Goal
Analyze TikTok datasets in `/Users/emilywebster/Dev/Entry tasks/tiktok_scrape/apify_downloads/` to identify valid datasets vs duplicates/failed runs.

## Initial Findings
- Found 163 total TikTok JSON files
- Multiple files appear to have the same search query but different timestamps
- Three distinct timestamp patterns visible: ~163X, ~1727, ~1741 (indicating multiple scraping sessions)

## TODO Items

### 1. File Inventory and Categorization
- [ ] Count total files excluding unknown files
- [ ] Extract unique search queries from filenames  
- [ ] Group files by search query
- [ ] Identify timestamp patterns to understand scraping sessions

### 2. Data Quality Analysis
- [ ] Check file sizes for each group
- [ ] Count video entries in each JSON file
- [ ] Identify files with 0 videos (failed runs)
- [ ] Compare video counts across duplicates of same query

### 3. Duplicate Detection
- [ ] For each search query, identify which file is most recent/complete
- [ ] Flag older/incomplete duplicates for removal consideration
- [ ] Create summary of valid vs duplicate files

### 4. Final Summary Report
- [ ] Provide count of unique search queries/datasets
- [ ] Calculate total valid videos across non-duplicate files  
- [ ] Recommend which files to use for video downloads
- [ ] Give accurate download progress estimate

## Expected Results
Based on user info: ~57 unique queries with 40-60 videos each = ~2,280-3,420 total videos expected

## Session Summary
Started analysis of TikTok scraping results to help user understand which datasets are valid vs duplicates from multiple scraping sessions.