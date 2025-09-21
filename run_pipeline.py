#!/usr/bin/env python3
"""
Simple runner script for TikTok Video Content Extraction Pipeline

Provides easy commands for testing and running the full pipeline.

Author: TikTok Content Analysis Pipeline
Created: January 3, 2025
"""

import os
import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    try:
        import cv2, pytesseract, whisper, pandas
        print("✅ Python packages: OK")
    except ImportError as e:
        print(f"❌ Missing Python package: {e}")
        return False
    
    # Check system tools
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg: OK")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found or not working")
        return False
    
    try:
        subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
        print("✅ Tesseract: OK")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Tesseract not found or not working")
        return False
    
    return True


def test_pipeline():
    """Run pipeline on 10 videos for testing."""
    print("🧪 Running pipeline test (10 videos)...")
    
    if not check_dependencies():
        return False
    
    pipeline_dir = Path(__file__).parent / "video_content_extraction"
    pipeline_script = pipeline_dir / "pipeline_controller.py"
    
    if not pipeline_script.exists():
        print(f"❌ Pipeline script not found: {pipeline_script}")
        return False
    
    # Run pipeline in test mode
    cmd = [
        sys.executable, 
        str(pipeline_script),
        "--test",
        "--log-level", "INFO"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=str(Path(__file__).parent))
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running pipeline: {e}")
        return False


def run_full_pipeline():
    """Run pipeline on all videos."""
    print("🚀 Running full pipeline...")
    
    if not check_dependencies():
        return False
    
    pipeline_dir = Path(__file__).parent / "video_content_extraction"
    pipeline_script = pipeline_dir / "pipeline_controller.py"
    
    if not pipeline_script.exists():
        print(f"❌ Pipeline script not found: {pipeline_script}")
        return False
    
    # Run full pipeline
    cmd = [
        sys.executable, 
        str(pipeline_script),
        "--workers", "8",
        "--batch-size", "100",
        "--log-level", "INFO"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=str(Path(__file__).parent))
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running pipeline: {e}")
        return False


def show_status():
    """Show current processing status."""
    output_dir = Path(__file__).parent / "extracted_content"
    csv_file = output_dir / "video_content_analysis.csv"
    progress_file = output_dir / "progress" / "progress.json"
    
    print("📊 Pipeline Status:")
    
    if csv_file.exists():
        try:
            import pandas as pd
            df = pd.read_csv(csv_file)
            total_processed = len(df)
            successful = len(df[df['processing_status'] == 'success'])
            partial = len(df[df['processing_status'] == 'partial'])
            failed = len(df[df['processing_status'] == 'failed'])
            
            print(f"   Total processed: {total_processed}")
            print(f"   Successful: {successful}")
            print(f"   Partial: {partial}")
            print(f"   Failed: {failed}")
            
            if total_processed > 0:
                success_rate = (successful / total_processed) * 100
                print(f"   Success rate: {success_rate:.1f}%")
        except Exception as e:
            print(f"   Error reading CSV: {e}")
    else:
        print("   No results file found")
    
    if progress_file.exists():
        try:
            import json
            with open(progress_file) as f:
                progress = json.load(f)
            print(f"   Current progress: {progress.get('completed_videos', 0)}/{progress.get('total_videos', 0)}")
        except Exception as e:
            print(f"   Error reading progress: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("TikTok Video Content Extraction Pipeline")
        print("")
        print("Usage:")
        print("  python run_video_extraction.py test       # Test with 10 videos")
        print("  python run_video_extraction.py run        # Run full pipeline")
        print("  python run_video_extraction.py status     # Show current status")
        print("  python run_video_extraction.py check      # Check dependencies")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "check":
        success = check_dependencies()
        sys.exit(0 if success else 1)
    
    elif command == "test":
        success = test_pipeline()
        sys.exit(0 if success else 1)
    
    elif command == "run":
        success = run_full_pipeline()
        sys.exit(0 if success else 1)
    
    elif command == "status":
        show_status()
        sys.exit(0)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()