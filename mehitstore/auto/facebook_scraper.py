#!/usr/bin/env python3
import asyncio
import json
import random
import re
import os
import sys
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CacheMode  # Fixed: Added CacheMode
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig
from bs4 import BeautifulSoup

async def hacker_style_facebook_scrape():
    """
    Advanced Facebook scraper with anti-detection techniques
    """
    
    print("🔧 Initializing Facebook scraper...")
    
    # Step 1: Configure browser for maximum stealth
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=False,
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport_width=1920,
        viewport_height=1080,
        verbose=True,
        extra_args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-web-security",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--no-default-browser-check",
        ]
    )
    
    # Step 2: Load pre-exported cookies
    cookie_file = Path("facebook_cookies.json")
    if not cookie_file.exists():
        print("\n❌ No cookies found. Please export cookies first!")
        return None
    
    try:
        with open(cookie_file, "r") as f:
            cookies = json.load(f)
        print(f"✅ Loaded {len(cookies)} cookies from file")
        
        print("\n📋 Cookie preview (first 3):")
        for i, cookie in enumerate(cookies[:3]):
            print(f"   Cookie {i+1}: {cookie.get('name')} = {cookie.get('value')[:20]}...")
            
    except Exception as e:
        print(f"❌ Error loading cookies: {e}")
        return None
    
    # Step 3: Configure the crawl
    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Now CacheMode is properly imported
        cookies=cookies,
        js_code="""
        // Wait for page to load
        await new Promise(r => setTimeout(r, 5000));
        
        // Check if we're logged in
        const isLoggedIn = !document.body.innerHTML.includes('login');
        console.log('Login status:', isLoggedIn ? 'Logged in' : 'Not logged in');
        
        // Scroll slowly
        let totalHeight = 0;
        const distance = 300;
        const scrollDelay = 1000;
        
        while (totalHeight < document.body.scrollHeight) {
            window.scrollBy(0, distance);
            totalHeight += distance;
            await new Promise(r => setTimeout(r, scrollDelay));
            if (totalHeight > 2000) break;
        }
        """,
        wait_until="networkidle",
        scan_full_page=True,
    )
    
    # Step 4: Execute
    print("\n🚀 Launching stealth browser...")
    print("📱 A browser window will open. Don't close it manually!")
    print("⏳ This may take 10-30 seconds...\n")
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url="https://web.facebook.com/ODPCKenya/",
                config=crawl_config
            )
            
            if result.success:
                print("✅ Page loaded successfully!")
                
                # Check login status
                html_lower = result.html.lower()
                if "login" not in html_lower:
                    print("✅ SUCCESS! Accessed the page while logged in!")
                    
                    # Save HTML
                    output_file = "facebook_page_content.html"
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(result.html)
                    print(f"💾 Saved HTML to {output_file}")
                    
                    # Extract posts
                    try:
                        soup = BeautifulSoup(result.html, 'html.parser')
                        
                        # Find posts
                        posts = soup.find_all('div', {'role': 'article'})
                        if not posts:
                            posts = soup.find_all('div', {'class': re.compile(r'userContent|post|story')})
                        
                        print(f"\n📊 Found {len(posts)} potential posts")
                        
                        # Save posts
                        posts_file = "extracted_posts.txt"
                        with open(posts_file, "w", encoding="utf-8") as f:
                            for i, post in enumerate(posts[:20]):
                                text = post.get_text(strip=True)
                                if text and len(text) > 50:
                                    f.write(f"{'='*60}\n")
                                    f.write(f"Post {i+1}\n")
                                    f.write(f"{'='*60}\n")
                                    f.write(f"{text}\n\n")
                        
                        print(f"💾 Saved posts to {posts_file}")
                        
                    except Exception as e:
                        print(f"⚠️ Post extraction error: {e}")
                    
                    return result.html
                else:
                    print("❌ Redirected to login page - cookies invalid")
            else:
                print(f"❌ Crawl failed: {result.error_message}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    return None

async def main():
    print("🐍 Facebook Scraper for Linux")
    print("=" * 60)
    html = await hacker_style_facebook_scrape()
    if html:
        print("\n✅ Scraping completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
