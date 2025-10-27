# How to Set Up Your API Key

## 📝 Get Your Free API Key

1. **Visit collegefootballdata.com**
   - Go to: https://collegefootballdata.com/
   
2. **Click "Key" in the top navigation**
   
3. **Sign up for a free account**
   - Provide your email address
   - Create a password
   - Verify your email
   
4. **Generate your API key**
   - Once logged in, click "Generate Key"
   - Copy your API key (it will look like a long string of letters and numbers)
   
## 🔧 Add Your API Key to the Project

### Method 1: Edit config.yaml (Recommended)

1. Open the file: `config/config.yaml`

2. Find this section:
   ```yaml
   collegefootballdata:
     api_key: ""  # Add your API key here
   ```

3. Paste your API key between the quotes:
   ```yaml
   collegefootballdata:
     api_key: "your_actual_api_key_goes_here"
   ```

4. Save the file

### Method 2: Environment Variable (Advanced)

Set as environment variable:

**Windows PowerShell:**
```powershell
$env:CFB_API_KEY="your_api_key_here"
```

**Windows Command Prompt:**
```cmd
set CFB_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export CFB_API_KEY="your_api_key_here"
```

Then modify `config/__init__.py` to read from environment:
```python
import os
api_key = os.getenv('CFB_API_KEY', '')
```

## ✅ Test Your API Key

Run this command to verify your API key works:

```bash
python collect_data.py --test-api
```

You should see:
```
✓ API connection successful! Found 133 teams.
```

If you see an error, double-check that:
1. You copied the entire API key
2. The key is between quotes in config.yaml
3. There are no extra spaces before or after the key

## 🔒 Keep Your API Key Secret

**Important:** Never share your API key publicly or commit it to version control!

The `.gitignore` file is configured to prevent `config/config.yaml` from being committed to Git.

## 📊 API Rate Limits

**Free Tier:**
- 60 requests per minute
- Unlimited daily requests
- Access to all endpoints

The data collection system automatically respects rate limits.

## ❓ Troubleshooting

### "Invalid API key" Error
- Double-check you copied the entire key
- Make sure there are no extra spaces
- Generate a new key if needed

### "Rate limit exceeded" Error
- The system will automatically wait and retry
- This is normal during large data collections

### Can't Find Your Key?
- Log back into collegefootballdata.com
- Click "Key" in the navigation
- Your existing key will be displayed
- You can generate a new one if needed

---

## 🎉 You're Ready!

Once your API key is configured and tested, you can start collecting data:

```bash
# Collect data for 2023 season
python collect_data.py --year 2023

# Or collect specific teams
python collect_data.py --year 2023 --teams Alabama Georgia
```

---

*For more information, see DATA_INGESTION_GUIDE.md*

