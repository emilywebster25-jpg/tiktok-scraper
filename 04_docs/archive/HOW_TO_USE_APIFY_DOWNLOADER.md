# How to Download Your TikTok Data from Apify

## Step-by-Step Instructions (Super Simple!)

### Step 1: Get Your Apify API Key

1. Go to: https://console.apify.com/account/integrations
2. Log in to your Apify account
3. You'll see something called "Personal API tokens"
4. Copy the long string of letters and numbers (it looks like: `apify_api_aBcDeFgHiJkLmNoPqRsTuVwXyZ`)

### Step 2: Add Your API Key to the Script

1. Open the file `download_apify_data.py` (it's in this same folder)
   - On Mac: Right-click the file → Open With → TextEdit
   - On Windows: Right-click the file → Open With → Notepad

2. Find this line near the top:
   ```
   APIFY_API_KEY = "YOUR_API_KEY_HERE"
   ```

3. Replace `YOUR_API_KEY_HERE` with your actual API key (keep the quotes!)
   
   It should look like:
   ```
   APIFY_API_KEY = "apify_api_aBcDeFgHiJkLmNoPqRsTuVwXyZ"
   ```

4. Save the file (Cmd+S on Mac, Ctrl+S on Windows)

### Step 3: Install What You Need (One Time Only)

1. Open Terminal (Mac) or Command Prompt (Windows)
   - Mac: Press Cmd+Space, type "Terminal", press Enter
   - Windows: Press Windows key, type "cmd", press Enter

2. Copy and paste this command, then press Enter:
   ```
   pip3 install requests
   ```

3. If it says "requirement already satisfied", that's perfect!

### Step 4: Run the Script

1. In Terminal/Command Prompt, navigate to the tiktok_scrape folder:
   ```
   cd "/Users/emilywebster/Dev/Entry tasks/tiktok_scrape"
   ```

2. Run the script:
   ```
   python3 download_apify_data.py
   ```

3. Watch as it downloads all your TikTok data!

### What Happens Next?

- The script will create a folder called `apify_downloads`
- Each file will be named with the search keyword (e.g., `tiktok_cardio_hiit_20250801.json`)
- You'll see a summary showing which searches you have

### Example Output:
```
🚀 Starting Apify TikTok Data Download
==================================================
🔍 Getting list of datasets from Apify...
📊 Found 15 datasets
==================================================
📥 Downloading dataset: TikTok Scraper Run
   Search query: cardio hiit
   ✅ Saved to: apify_downloads/tiktok_cardio_hiit_20250801_143022.json

📋 DOWNLOAD SUMMARY
==================================================
🔍 Search: 'cardio hiit'
   - apify_downloads/tiktok_cardio_hiit_20250801_143022.json
```

### Troubleshooting

**"Please check your API key is correct"**
- Make sure you copied the entire API key
- Check there are no extra spaces
- Make sure you kept the quotes around it

**"No datasets found"**
- Make sure you're using the right Apify account
- Check if you have any datasets in your Apify console

**"pip3: command not found"**
- You might need to install Python first
- Go to python.org and download Python 3

### Need Help?

If something doesn't work, tell me:
1. What step you're on
2. What error message you see
3. I'll help you fix it!