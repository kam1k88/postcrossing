#!/usr/bin/env python3
"""Upload TimeData.csv to Hugging Face dataset"""

import os
import sys
from huggingface_hub import HfApi

def main():
    # Get token from environment
    token = os.environ.get('HF_TOKEN', '').strip()
    
    if not token:
        print("❌ Error: HF_TOKEN environment variable is not set or empty")
        sys.exit(1)
    
    print(f"🔑 Token found (length: {len(token)} chars)")
    
    # Upload file
    try:
        api = HfApi()
        print("📤 Uploading docs/TimeData.csv to Hugging Face...")
        
        api.upload_file(
            path_or_fileobj='docs/TimeData.csv',
            path_in_repo='TimeData.csv',
            repo_id='kamjke/postcrossing-daily-growth',
            repo_type='dataset',
            token=token,
            commit_message='Automated update from GitHub Actions'
        )
        
        print('✅ Successfully uploaded to Hugging Face!')
        
    except Exception as e:
        print(f"❌ Error uploading to Hugging Face: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
