#!/usr/bin/env python3
import os
import json
from datetime import datetime, timedelta
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def scrape_facebook_page_posts():
    """
    Use Apify's Facebook Posts Scraper to get actual posts with dates
    """
    print("=" * 70)
    print("📱 ODPC Kenya - Professional Facebook Scraper")
    print("=" * 70)
    
    # Get API token from environment
    APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
    if not APIFY_API_TOKEN:
        print("❌ Please set your APIFY_API_TOKEN in .env file")
        print("\n📝 How to get one:")
        print("1. Sign up at https://apify.com")
        print("2. Go to Settings → API & Integrations")
        print("3. Copy your API token")
        return
    
    # Initialize Apify client
    client = ApifyClient(APIFY_API_TOKEN)
    
    # Calculate date 10 days ago
    ten_days_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    
    print(f"\n🔍 Searching for posts from: {ten_days_ago} to today")
    
    # Prepare input for Facebook Posts Scraper
    run_input = {
        "pageUrls": ["https://www.facebook.com/ODPCKenya/"],
        "maxPostsPerPage": 50,  # Get up to 50 posts
        "includeComments": True,
        "maxCommentsPerPost": 5,
        "dateFrom": ten_days_ago,  # Only posts from last 10 days
        "dateTo": datetime.now().strftime("%Y-%m-%d"),
        "contentType": "all",  # Include all content types
        "skipSponsored": True,  # Skip sponsored content
        "demoMode": False,
    }
    
    print("\n🚀 Running Facebook scraper (this may take 1-2 minutes)...")
    
    try:
        # Run the actor and wait for results
        run = client.actor("alizarin_refrigerator-owner/facebook-page-post-scraper").call(run_input=run_input)
        
        # Fetch results from dataset
        print("✅ Scraping complete! Processing results...")
        
        # Prepare output files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"odpckenya_posts_{timestamp}.json"
        text_file = f"odpckenya_posts_{timestamp}.txt"
        
        posts_found = 0
        all_posts = []
        
        # Iterate through results
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            all_posts.append(item)
            posts_found += 1
            
            # Print progress
            if posts_found <= 5:  # Show first 5 posts
                print(f"\n📌 Post #{posts_found}:")
                print(f"   Date: {item.get('publishedAt', 'Unknown')}")
                print(f"   Content: {item.get('content', '')[:150]}...")
                if item.get('imageUrls'):
                    print(f"   Images: {len(item['imageUrls'])}")
                if item.get('videoUrl'):
                    print(f"   Video: Yes")
        
        # Save full JSON data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_posts, f, indent=2, ensure_ascii=False)
        
        # Save readable text format
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("ODPC KENYA - FACEBOOK POSTS (Last 10 Days)\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Posts found: {posts_found}\n")
            f.write("=" * 70 + "\n\n")
            
            for i, post in enumerate(all_posts, 1):
                f.write(f"POST #{i}\n")
                f.write(f"Date: {post.get('publishedAt', 'Unknown')}\n")
                f.write("-" * 40 + "\n")
                f.write(f"{post.get('content', 'No content')}\n\n")
                
                if post.get('imageUrls'):
                    f.write(f"Images ({len(post['imageUrls'])}):\n")
                    for img_url in post['imageUrls'][:3]:
                        f.write(f"  • {img_url[:100]}...\n")
                    f.write("\n")
                
                if post.get('videoUrl'):
                    f.write(f"Video: {post['videoUrl']}\n\n")
                
                if post.get('reactions'):
                    f.write("Reactions:\n")
                    for reaction, count in post['reactions'].items():
                        if count > 0:
                            f.write(f"  • {reaction}: {count}\n")
                    f.write("\n")
                
                if post.get('comments'):
                    f.write(f"Comments ({len(post['comments'])}):\n")
                    for comment in post['comments'][:3]:
                        f.write(f"  • {comment.get('text', '')[:100]}...\n")
                    f.write("\n")
                
                f.write("=" * 70 + "\n\n")
        
        print(f"\n✅ Success! Found {posts_found} posts from the last 10 days")
        print(f"📁 JSON data saved to: {output_file}")
        print(f"📁 Readable text saved to: {text_file}")
        
        # Summary statistics
        posts_with_images = sum(1 for p in all_posts if p.get('imageUrls'))
        posts_with_videos = sum(1 for p in all_posts if p.get('videoUrl'))
        total_reactions = sum(p.get('reactions', {}).get('total', 0) for p in all_posts)
        
        print("\n📊 Summary:")
        print(f"   • Posts with images: {posts_with_images}")
        print(f"   • Posts with videos: {posts_with_videos}")
        print(f"   • Total reactions: {total_reactions}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check your API token is correct")
        print("2. Make sure you have credits in your Apify account")
        print("3. Try with demoMode: true first to test")

def setup_environment():
    """
    Create .env file template
    """
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("# Apify API Token\n")
            f.write("# Get it from: https://console.apify.com/settings/integrations\n")
            f.write('APIFY_API_TOKEN="your-api-token-here"\n')
        print("✅ Created .env file template")
        print("📝 Please edit it and add your Apify API token")
        return False
    return True

if __name__ == "__main__":
    if setup_environment():
        scrape_facebook_page_posts()
    else:
        print("\nAfter adding your API token to .env, run this script again.")
