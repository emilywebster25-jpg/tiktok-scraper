# 🔄 How to Restart TikTok Video Downloads

## If Claude Code Window Closes

**Quick Steps:**
1. Open Terminal/Command Prompt
2. Run: `cd "/Users/emilywebster/Dev/Entry tasks/tiktok_scrape"`
3. Run: `python3 download_videos.py`

The script will automatically continue from where it left off!

## If You Want to Talk to Claude Again

**Option 1: Restart Claude Code**
```bash
claude-code
```

**Option 2: Tell Claude What You Need**
Say: *"My TikTok video download script stopped. I need to restart it. The script is at /Users/emilywebster/Dev/Entry tasks/tiktok_scrape/download_videos.py"*

## Current Status When This Was Written
- ✅ 72 videos downloaded (354MB)
- 📊 1,820 total videos to download
- 💾 ~11GB total space needed (you have 317GB available)
- 🎯 Script: `download_videos.py` in tiktok_scrape folder

## Quick Check Progress
```bash
cd "/Users/emilywebster/Dev/Entry tasks/tiktok_scrape"
ls videos/ | wc -l
```
This shows how many videos you've downloaded.

## Files Being Downloaded
- **Videos**: `videos/` folder (.mp4 files)
- **Cover images**: `covers/` folder (.jpg files)  
- **Music**: `music/` folder (.mp3 files)
- **Metadata**: `videos/` folder (*_metadata.json files)

✅ **The script is smart - it won't re-download existing files!**