#!/bin/bash
# Overnight TikTok Download Pipeline
# Runs after current process completes

echo "🌙 Starting overnight download pipeline..."
echo "⏰ Started at: $(date)"

cd "/Users/emilywebster/Dev/Entry tasks/tiktok_scrape"

# Wait for current process to complete
echo "⏳ Waiting for current video assessment to complete..."
while pgrep -f "download_videos.py" > /dev/null; do
    sleep 30
    echo "   Still running... $(date)"
done

echo "✅ Phase 1 complete - Current video assessment finished"
echo "🔄 Starting Phase 2 - Downloading new Apify datasets..."

# Phase 2: Download new datasets
python3 download_apify_data.py >> overnight_log.txt 2>&1
echo "✅ Phase 2 complete - New datasets downloaded"

echo "🎬 Starting Phase 3 - Processing all videos (old + new)..."

# Phase 3: Process all videos
python3 download_videos.py >> overnight_log.txt 2>&1
echo "✅ Phase 3 complete - All videos processed"

echo "🎉 Overnight pipeline complete at: $(date)"
echo "📊 Final stats:"
find videos/ -name "*.mp4" | wc -l
echo "videos downloaded"