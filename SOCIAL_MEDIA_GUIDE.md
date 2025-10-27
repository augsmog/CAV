# Social Media Data Collection Guide

## Overview

The CAV model uses social media metrics to calculate player brand value and NIL potential. This guide explains how to collect and import social media data.

## Data Collection Methods

### Method 1: Manual CSV Import (Recommended)

The easiest way to add social media data is through a CSV file.

#### Step 1: Get the Template

```bash
python scrapers/enhanced_social_scraper.py
```

This creates `data/social_media_template.csv` with the following format:

```csv
player_name,team,instagram_handle,twitter_handle,tiktok_handle,instagram_followers,twitter_followers,tiktok_followers,engagement_rate,notes
Caleb Williams,USC,calebwilliams,CALEBcsw,calebwilliams,500000,250000,100000,0.045,Example data
```

#### Step 2: Fill in Player Data

Edit the CSV file with real player data:

**player_name**: Full name (must match database)  
**team**: Team name  
**instagram_handle**: Instagram username (without @)  
**twitter_handle**: Twitter/X username (without @)  
**tiktok_handle**: TikTok username (without @)  
**instagram_followers**: Current follower count  
**twitter_followers**: Current follower count  
**tiktok_followers**: Current follower count  
**engagement_rate**: Average engagement rate (0.03 = 3%)  
**notes**: Optional notes  

#### Step 3: Import to Database

```python
from scrapers.enhanced_social_scraper import EnhancedSocialMediaScraper
from database import get_session
from database.models import Player, SocialMedia

scraper = EnhancedSocialMediaScraper()
session = get_session()

# Load CSV
social_data = scraper.load_handles_from_csv('data/player_social_media.csv')

# Import to database
for data in social_data:
    # Find player
    player = session.query(Player).filter(
        Player.name.ilike(f"%{data['player_name']}%")
    ).first()
    
    if player:
        # Check if social media record exists
        existing = session.query(SocialMedia).filter_by(player_id=player.id).first()
        
        if existing:
            # Update
            existing.instagram_handle = data.get('instagram_handle')
            existing.twitter_handle = data.get('twitter_handle')
            existing.tiktok_handle = data.get('tiktok_handle')
            existing.instagram_followers = data.get('instagram_followers')
            existing.twitter_followers = data.get('twitter_followers')
            existing.tiktok_followers = data.get('tiktok_followers')
        else:
            # Create new
            social_media = SocialMedia(
                player_id=player.id,
                instagram_handle=data.get('instagram_handle'),
                twitter_handle=data.get('twitter_handle'),
                tiktok_handle=data.get('tiktok_handle'),
                instagram_followers=data.get('instagram_followers'),
                twitter_followers=data.get('twitter_followers'),
                tiktok_followers=data.get('tiktok_followers')
            )
            session.add(social_media)

session.commit()
print("Social media data imported!")
```

### Method 2: Web Scraping (Limited)

**Note**: Both Instagram and Twitter heavily restrict web scraping. This method is best-effort only.

```python
scraper = EnhancedSocialMediaScraper()

# Try to scrape public data
instagram_data = scraper.scrape_instagram_public('calebwilliams')
if instagram_data:
    print(f"Followers: {instagram_data['followers']}")
```

### Method 3: Official APIs (Production Use)

For production use, integrate official APIs:

#### Instagram Graph API
- Requires Facebook Developer Account
- Apply for Instagram Basic Display API access
- Rate limit: 200 calls/hour

#### Twitter API v2
- Sign up at [developer.twitter.com](https://developer.twitter.com)
- Essential tier: 500,000 tweets/month
- Elevated tier: $100/month for more access

#### TikTok For Developers
- Apply at [developers.tiktok.com](https://developers.tiktok.com)
- Limited to business/creator accounts
- Rate limits vary by endpoint

## Finding Player Handles

### Automated Handle Search

```python
scraper = EnhancedSocialMediaScraper()
results = scraper.search_player_handles("Bo Nix", "Oregon")
print(results['probable_handles'])
# ['bonix', 'bo_nix', 'bo.nix', 'bnix', 'bo_n', 'nixb']
```

### Manual Verification

1. Google: `"[Player Name]" [Team] Instagram`
2. Check team rosters (often link to social media)
3. Use On3 or 247Sports player profiles
4. Check NIL marketplaces (Opendorse, INFLCR)

## Social Media Metrics Explained

### Follower Counts
- **Instagram**: Highest engagement, most valuable
- **TikTok**: Viral potential, younger audience
- **Twitter**: News and updates, lower engagement

### Engagement Rate
Calculate as: (Likes + Comments) / Followers / Posts

Typical rates:
- **Excellent**: > 5%
- **Good**: 3-5%
- **Average**: 1-3%
- **Poor**: < 1%

### Weighted Scoring
The model uses weighted followers:
- Instagram: 1.5x weight
- TikTok: 1.3x weight
- Twitter: 1.0x weight

A player with 100k Instagram = 150k weighted followers

## Data Sources

### Recommended Sources
1. **On3 NIL Valuations** - on3.com/nil/
2. **247Sports Profiles** - 247sports.com
3. **Team Rosters** - Often link social media
4. **Opendorse** - opendorse.com (NIL marketplace)
5. **INFLCR** - inflcr.com (team management platform)

### Manual Data Collection Tools

**Social Blade** (socialblade.com)
- Historical follower data
- Growth tracking
- Free tier available

**HypeAuditor** (hypeauditor.com)
- Engagement analysis
- Audience demographics
- Paid service

## CSV Import Script

Save as `import_social_media.py`:

```python
from scrapers.enhanced_social_scraper import EnhancedSocialMediaScraper
from database import get_session
from database.models import Player, SocialMedia

def import_social_media_from_csv(csv_file):
    scraper = EnhancedSocialMediaScraper()
    session = get_session()
    
    data_list = scraper.load_handles_from_csv(csv_file)
    
    added = 0
    updated = 0
    failed = 0
    
    for data in data_list:
        try:
            player = session.query(Player).filter(
                Player.name.ilike(f"%{data['player_name']}%")
            ).first()
            
            if not player:
                print(f"Player not found: {data['player_name']}")
                failed += 1
                continue
            
            existing = session.query(SocialMedia).filter_by(
                player_id=player.id
            ).first()
            
            if existing:
                existing.instagram_handle = data.get('instagram_handle')
                existing.twitter_handle = data.get('twitter_handle')
                existing.tiktok_handle = data.get('tiktok_handle')
                existing.instagram_followers = data.get('instagram_followers')
                existing.twitter_followers = data.get('twitter_followers')
                existing.tiktok_followers = data.get('tiktok_followers')
                total = (existing.instagram_followers or 0) + (existing.twitter_followers or 0) + (existing.tiktok_followers or 0)
                existing.total_followers = total
                updated += 1
            else:
                total = (data.get('instagram_followers') or 0) + (data.get('twitter_followers') or 0) + (data.get('tiktok_followers') or 0)
                social_media = SocialMedia(
                    player_id=player.id,
                    instagram_handle=data.get('instagram_handle'),
                    twitter_handle=data.get('twitter_handle'),
                    tiktok_handle=data.get('tiktok_handle'),
                    instagram_followers=data.get('instagram_followers'),
                    twitter_followers=data.get('twitter_followers'),
                    tiktok_followers=data.get('tiktok_followers'),
                    total_followers=total
                )
                session.add(social_media)
                added += 1
        
        except Exception as e:
            print(f"Error processing {data.get('player_name')}: {e}")
            failed += 1
    
    session.commit()
    
    print(f"\n{'='*70}")
    print(f"Import complete!")
    print(f"Added: {added}")
    print(f"Updated: {updated}")
    print(f"Failed: {failed}")
    print(f"{'='*70}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        import_social_media_from_csv(csv_file)
    else:
        print("Usage: python import_social_media.py <csv_file>")
```

## Best Practices

1. **Update Regularly**: Social media changes quickly, update monthly
2. **Verify Handles**: Always verify before importing
3. **Track Changes**: Keep historical data for growth rates
4. **Respect Privacy**: Only collect public information
5. **Rate Limit**: Don't overwhelm platforms with requests

## Example: Top 25 Players

Create `data/top_players_social.csv` with data for:
- Top QBs (Caleb Williams, Bo Nix, etc.)
- Heisman candidates
- High-profile transfers
- Team captains

This provides enough data for meaningful brand valuations.

## Troubleshooting

**"Player not found"**: Check name spelling matches database exactly

**"API rate limited"**: Wait 1-2 minutes between scraping attempts

**"Invalid CSV format"**: Ensure headers match template exactly

**"Missing engagement rate"**: Use default 0.03 (3%) if unknown

## Next Steps

After importing social media data:
1. Re-run valuations: `python test_model_valuations.py`
2. Check brand scores in output JSON
3. Compare with known NIL deals
4. Adjust engagement rates as needed

---

**Note**: Social media data significantly impacts brand and NIL valuations. Even partial data (top 50-100 players) provides meaningful insights.

