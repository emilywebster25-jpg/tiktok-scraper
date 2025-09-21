# 🚨 URGENT: Download TikTok Videos Before Apify Subscription Expires

## Quick Start (Do This NOW!)

1. **Open Terminal/Command Prompt**
   ```bash
   cd "/Users/emilywebster/Dev/Entry tasks/tiktok_scrape"
   ```

2. **Run the video download script**
   ```bash
   python3 download_videos.py
   ```

3. **Let it run** - it will download ALL videos from your 40 TikTok datasets

## What This Script Does

- **Downloads video files** (.mp4) from Apify servers to local `videos/` folder
- **Downloads cover images** (.jpg) from TikTok to local `covers/` folder  
- **Downloads music/audio** (.mp3) from TikTok to local `music/` folder
- **Saves metadata** (.json) for each video with all the original data
- **Uses your existing API key** already configured in the script
- **Organizes files** by search query and video ID

## File Organization

Your downloads will be organized like this:
```
tiktok_scrape/
├── videos/
│   ├── calisthenics_workout_plan_men_kingscommunity4_7224926193940778283.mp4
│   ├── dumbbell_cardio_women_fitnessblender_7234567890123456789.mp4
│   └── [video_metadata.json files for each video]
├── covers/
│   ├── calisthenics_workout_plan_men_kingscommunity4_7224926193940778283_cover.jpg
│   └── [cover images for each video]
└── music/
    ├── calisthenics_workout_plan_men_kingscommunity4_7224926193940778283_SPIT_IN_MY_FACE.mp3
    └── [music files for each video]
```

## Expected Results

Based on your 40 datasets, you should get:
- **~1,000-2,000 video files** (varies by dataset size)
- **Same number of cover images**
- **Music files** (where available)
- **Complete metadata** preserved for each video

## Time Estimate

- **Small datasets** (50 videos): ~5-10 minutes
- **Large datasets** (200+ videos): ~20-30 minutes  
- **All 40 datasets**: Probably 2-4 hours total

## If Something Goes Wrong

### "Permission denied" or "API key" errors:
- Make sure you're in the right directory
- Check that your Apify subscription is still active

### "File not found" errors:
- Run `ls apify_downloads/` to make sure the JSON files are there
- Make sure you ran `download_apify_data.py` first

### Downloads are slow:
- This is normal! Each video is several MB
- The script includes delays to be nice to servers
- Let it run in the background

### Want to check progress:
- The script prints progress as it goes
- You can check the `videos/` folder to see files being downloaded
- Press Ctrl+C if you need to stop (you can restart later)

## 🚨 DO THIS BEFORE YOUR SUBSCRIPTION EXPIRES!

Once your Apify subscription expires, those video URLs will stop working and you'll lose access to all the video content forever. The script preserves everything locally so you can analyze the videos even after your subscription ends.

## After Download Completes

You'll have:
- ✅ All video content saved locally
- ✅ All metadata preserved
- ✅ Files organized by search query
- ✅ No dependency on Apify subscription
- ✅ Ready for video content analysis

**Just run the script and let it do its thing!** 🚀