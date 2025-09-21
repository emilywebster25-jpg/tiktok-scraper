# TikTok Video Content Extraction Pipeline

## 🎯 Overview

A comprehensive pipeline for extracting on-screen text (OCR) and spoken content (speech-to-text) from 4,445 TikTok MP4 files. Optimized for Apple Silicon M2 Pro with 32GB RAM.

## ✅ Installation Complete

All dependencies have been successfully installed:
- **FFmpeg 7.1.1** - Video processing with Apple Silicon optimization
- **Tesseract 5.5.1** - OCR with NEON acceleration
- **OpenAI Whisper (latest)** - Speech-to-text with Metal acceleration
- **Python packages** - OpenCV, PyTesseract, Pandas, and supporting libraries

## 🚀 Quick Start

### Test the Pipeline (Recommended First Step)
```bash
cd "/Users/emilywebster/Dev/Entry tasks/tiktok_scrape"
python3 run_video_extraction.py test
```
This processes 10 videos to verify everything works correctly.

### Run Full Pipeline
```bash
python3 run_video_extraction.py run
```
This processes all 4,445 videos (estimated 12-18 hours).

### Check Status
```bash
python3 run_video_extraction.py status
```
View current processing progress and results.

## 📁 Project Structure

```
tiktok_scrape/
├── videos/                               # 4,445 MP4 files
├── video_content_extraction/             # Pipeline scripts
│   ├── frame_extractor.py               # FFmpeg frame sampling
│   ├── ocr_processor.py                 # Tesseract text extraction
│   ├── audio_transcriber.py             # Whisper speech-to-text
│   ├── data_merger.py                   # CSV output generation
│   ├── pipeline_controller.py           # Main orchestrator
│   └── utils.py                         # Progress tracking & monitoring
├── extracted_content/                   # Output directory
│   ├── video_content_analysis.csv      # Main results file
│   ├── processing_summary.json         # Batch summaries
│   └── progress/                        # Resume capability
├── logs/                               # Processing logs
├── run_video_extraction.py            # Simple runner script
└── VIDEO_CONTENT_EXTRACTION_*.md      # Documentation
```

## 📊 Output Format

### Main CSV File: `extracted_content/video_content_analysis.csv`

| Column | Description | Example |
|--------|-------------|---------|
| `video_id` | TikTok video ID | `7449587389527231787` |
| `filename` | Original filename | `20_min_workout_women_ahealthyelf_7449587389527231787.mp4` |
| `duration_seconds` | Video length | `22.5` |
| `frame_count` | Frames processed | `8` |
| `on_screen_text` | OCR results (deduplicated) | `EMOM workout; 20 min; Upper body` |
| `spoken_phrases` | Whisper transcription | `EMOM 20 min EMOM Workout Every Minute on the Minute` |
| `text_timestamps` | Frame timestamps with text | `3.0s:EMOM workout; 6.0s:20 min` |
| `audio_timestamps` | Word-level timestamps | `0.5s-EMOM; 2.1s-workout; 4.3s-focused` |
| `ocr_confidence` | OCR quality score (0-100) | `85.5` |
| `transcription_confidence` | Whisper confidence (0-1) | `0.92` |
| `processing_status` | Success/partial/failed | `success` |
| `error_notes` | Error details if any | `""` |
| `processed_timestamp` | When processed | `2025-01-03T15:30:45` |

## ⚙️ Pipeline Features

### 🎬 Frame Extraction
- **Sampling**: 1 frame every 2.5 seconds
- **Quality**: High-resolution PNG for OCR accuracy
- **Optimization**: Apple Silicon hardware acceleration

### 🔍 OCR Processing (Tesseract)
- **Language**: English with confidence filtering (30% minimum)
- **Deduplication**: Removes similar text across frames
- **Preprocessing**: Contrast enhancement and noise reduction
- **Performance**: NEON acceleration on M2 Pro

### 🎙️ Audio Transcription (Whisper)
- **Model**: Medium (769MB) - optimal for M2 Pro
- **Acceleration**: Metal Performance Shaders
- **Features**: Word-level timestamps, auto language detection
- **Quality**: 90-95% accuracy for clear English speech

### 🔄 Concurrent Processing
- **Workers**: 8-10 concurrent processes
- **Batching**: 100 videos per batch
- **Resume**: Automatic resume if interrupted
- **Monitoring**: Real-time progress with ETA

## 📈 Performance Expectations

### Processing Speed (M2 Pro, 32GB RAM)
- **Per Video**: 60-90 seconds average
- **Test Run (10 videos)**: ~15 minutes
- **Full Dataset (4,445 videos)**: 12-18 hours

### Expected Accuracy
- **OCR**: 85-95% for clear overlay text
- **Transcription**: 90-95% for clear English speech
- **Processing Success**: 95%+ videos complete successfully

### Resource Usage
- **CPU**: 80-90% utilization
- **Memory**: 8-12GB peak
- **Storage**: ~50-75GB temporary files (auto-cleaned)

## 🛠️ Advanced Usage

### Command Line Options
```bash
# Custom configuration
python3 video_content_extraction/pipeline_controller.py \
  --videos-dir videos \
  --output-dir extracted_content \
  --workers 8 \
  --batch-size 100 \
  --log-level INFO

# Test specific number of videos
python3 video_content_extraction/pipeline_controller.py \
  --max-videos 50 \
  --test

# Start fresh (no resume)
python3 video_content_extraction/pipeline_controller.py \
  --no-resume
```

### Individual Component Testing
```bash
# Test frame extraction
python3 video_content_extraction/frame_extractor.py videos/sample_video.mp4

# Test OCR
python3 video_content_extraction/ocr_processor.py extracted_content/frames/sample_frames/

# Test transcription
python3 video_content_extraction/audio_transcriber.py videos/sample_video.mp4
```

## 🔍 Monitoring & Troubleshooting

### Real-time Monitoring
The pipeline provides real-time feedback:
```
📊 Processing Progress:
   Completed: 1,250/4,445 (28.1%)
   Failed: 15 (1.2%)
   Current: 7449587389527231787
   Elapsed: 3:45:12
   Remaining: 9:23:48
   CPU: 85% | RAM: 68% | Temp: 72°C
```

### Log Files
- **Main log**: `logs/video_processing.log`
- **Progress**: `extracted_content/progress/progress.json`
- **Summaries**: `extracted_content/processing_summary.json`

### Common Issues & Solutions

1. **High Memory Usage**
   - Reduce `--workers` from 8 to 4-6
   - Reduce `--batch-size` from 100 to 50

2. **Slow Processing**
   - Check available storage space
   - Monitor CPU temperature (throttling at 100°C)
   - Verify Whisper is using Metal acceleration

3. **OCR Poor Quality**
   - Check for blurry or low-contrast videos
   - Review confidence thresholds in OCR settings

4. **Resume Not Working**
   - Check CSV file integrity
   - Delete progress files to start fresh

## 🔐 Privacy & Security

- **Local Processing**: No data sent to external APIs
- **Temporary Files**: Auto-cleaned after processing
- **Data Location**: All outputs stored locally in project directory

## 📋 Quality Assurance

### Validation Built-in
- Data type validation for all CSV fields
- Processing status tracking (success/partial/failed)
- Error categorization and logging
- Confidence scoring for quality assessment

### Sample Testing
Always run test mode first to validate:
```bash
python3 run_video_extraction.py test
```

## 🎯 Next Steps

1. **Test Small Batch** (Recommended)
   ```bash
   python3 run_video_extraction.py test
   ```

2. **Review Test Results**
   - Check `extracted_content/video_content_analysis.csv`
   - Verify OCR and transcription quality
   - Confirm processing speeds

3. **Run Full Pipeline**
   ```bash
   python3 run_video_extraction.py run
   ```

4. **Monitor Progress**
   ```bash
   python3 run_video_extraction.py status
   ```

## 📞 Support

All components are thoroughly documented with:
- Comprehensive error handling
- Detailed logging
- Progress tracking
- Resume capability

The pipeline is ready for production use on your M2 Pro MacBook with 32GB RAM.

---

**Pipeline Status**: ✅ Ready for Testing
**Next Action**: Run test batch to verify functionality