#!/usr/bin/env python3

import os
import argparse
import whisper
import shutil
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='Download Whisper models for offline use')
    parser.add_argument('--whisper-model', default='base', 
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Whisper model size to download')
    parser.add_argument('--output-dir', default='./models',
                        help='Directory to save models')
    return parser.parse_args()

def download_whisper_model(model_size, output_dir):
    print(f"Downloading Whisper {model_size} model...")
    
    # Create output directory
    whisper_dir = os.path.join(output_dir, 'whisper')
    os.makedirs(whisper_dir, exist_ok=True)
    
    # Download the model
    try:
        # This will download the model to the default cache directory
        # and then we'll load it to verify it works
        model = whisper.load_model(model_size)
        print(f"Whisper {model_size} model downloaded successfully!")
        
        # Get the model file paths
        model_files = []
        for root, dirs, files in os.walk(os.path.expanduser("~/.cache/whisper")):
            for file in files:
                if file.endswith(".pt") and model_size in file:
                    model_files.append(os.path.join(root, file))
        
        # Copy the model files to the output directory
        for file in model_files:
            dest_file = os.path.join(whisper_dir, os.path.basename(file))
            shutil.copy2(file, dest_file)
            print(f"Copied {file} to {dest_file}")
        
        return True
    except Exception as e:
        print(f"Error downloading Whisper model: {str(e)}")
        return False

def main():
    args = parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Download Whisper model
    success = download_whisper_model(args.whisper_model, args.output_dir)
    
    # Print summary
    print("\nDownload Summary:")
    print(f"Whisper model: {'Success' if success else 'Failed'}")
    
    if success:
        print("\nModel downloaded successfully!")
        print(f"Model saved to {os.path.abspath(args.output_dir)}")
    else:
        print("\nModel download failed. Please check the errors above.")

if __name__ == "__main__":
    main()