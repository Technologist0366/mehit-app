#!/usr/bin/env python3
import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig
from bs4 import BeautifulSoup
from datetime import datetime

async def extract_facebook_content():
    print("=" * 60)
    print("📱 Extracting ODPC Kenya Facebook Content")
    print("=" * 60)
    
    # Load cookies if available
    cookies = None
    try:
        with open("facebook_cookies_fixed.json", "r") as f:
            cookies = json.load(f)
        print(f"✅ Loaded {len(cookies)} cookies")
    except:
        print("⚠️ No cookies found, proceeding without authentication")
    
    # Browser config - optimized for faster loading
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,  # Run in background for speed
        cookies=cookies,
        verbose=False,
        viewport_width=1280,
        viewport_height=800
    )
    
    # Crawl config - with shorter timeout and simpler wait condition
    crawl_config = CrawlerRunConfig(
        cache_mode="bypass",
        wait_until="domcontentloaded",  # Faster than networkidle
        page_timeout=30000,  # 30 second timeout
        js_code="""
        // Minimal scrolling to trigger content
        window.scrollBy(0, 200);
        await new Promise(r => setTimeout(r, 1000));
        """
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("\n🌐 Attempting to fetch page (timeout: 30s)...")
        
        try:
            result = await crawler.arun(
                "https://www.facebook.com/ODPCKenya/",
                config=crawl_config
            )
            
            if result.success:
                print("✅ Page fetched successfully!")
                
                # Save with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                html_file = f"odpckenya_{timestamp}.html"
                
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(result.html)
                print(f"💾 Saved HTML to {html_file}")
                
                # Parse content
                soup = BeautifulSoup(result.html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get page title
                title = soup.find('title')
                if title:
                    print(f"\n📄 Page Title: {title.text}")
                
                # Extract all visible text
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                # Save all text
                text_file = f"odpckenya_text_{timestamp}.txt"
                with open(text_file, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"💾 Saved all text to {text_file}")
                
                # Try to find posts using common patterns
                print("\n🔍 Searching for posts...")
                
                # Method 1: Look for elements with post-like attributes
                post_containers = []
                
                # Common Facebook post containers
                patterns = [
                    ('div', {'data-testid': 'post_message'}),
                    ('div', {'role': 'article'}),
                    ('div', {'class': re.compile(r'userContent', re.I)}),
                    ('div', {'class': re.compile(r'post', re.I)}),
                    ('div', {'class': re.compile(r'story', re.I)})
                ]
                
                for tag, attrs in patterns:
                    found = soup.find_all(tag, attrs)
                    if found:
                        post_containers.extend(found)
                        print(f"  📌 Found {len(found)} with {tag} {attrs}")
                
                # Remove duplicates
                seen = set()
                unique_posts = []
                for post in post_containers:
                    post_id = id(post)
                    if post_id not in seen:
                        seen.add(post_id)
                        unique_posts.append(post)
                
                print(f"\n📊 Found {len(unique_posts)} potential post containers")
                
                # Extract post content
                posts_file = f"odpckenya_posts_{timestamp}.txt"
                post_count = 0
                
                with open(posts_file, "w", encoding="utf-8") as f:
                    f.write(f"ODPC KENYA FACEBOOK POSTS\n")
                    f.write(f"Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for i, post in enumerate(unique_posts[:30]):
                        # Get clean text
                        text = post.get_text(strip=True)
                        
                        # Clean up
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        clean_text = '\n'.join(lines)
                        
                        if clean_text and len(clean_text) > 50:
                            post_count += 1
                            f.write(f"POST #{post_count}\n")
                            f.write("-" * 40 + "\n")
                            f.write(clean_text)
                            f.write("\n\n" + "-" * 40 + "\n\n")
                
                if post_count > 0:
                    print(f"✅ Extracted {post_count} posts to {posts_file}")
                    
                    # Show preview
                    print("\n📝 First post preview:")
                    with open(posts_file, "r") as f:
                        preview = f.read().split('POST #2')[0]
                        print(preview[:300] + "...\n")
                else:
                    print("⚠️ No clear posts found. Check the text file for content.")
                    
            else:
                print(f"❌ Failed: {result.error_message}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
            # Try alternative URL
            print("\n🔄 Trying alternative URL (m.facebook.com)...")
            try:
                result = await crawler.arun(
                    "https://m.facebook.com/ODPCKenya/",  # Mobile version
                    config=crawl_config
                )
                
                if result.success:
                    print("✅ Mobile page fetched successfully!")
                    with open("odpckenya_mobile.html", "w", encoding="utf-8") as f:
                        f.write(result.html)
                    print("💾 Saved mobile HTML to odpckenya_mobile.html")
                else:
                    print("❌ Mobile page also failed")
            except:
                print("❌ All attempts failed")

async def main():
    await extract_facebook_content()
    print("\n✨ Extraction attempt complete!")

if __name__ == "__main__":
    asyncio.run(main())
