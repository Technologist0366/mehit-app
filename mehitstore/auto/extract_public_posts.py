#!/usr/bin/env python3
import asyncio
import json
import re
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig
from bs4 import BeautifulSoup

async def extract_public_facebook_content():
    print("=" * 60)
    print("📢 Extracting Public Content from ODPC Kenya Facebook Page")
    print("=" * 60)
    
    # Load cookies (even if they don't log us in, they might be needed to see the page)
    try:
        with open("facebook_cookies_fixed.json", "r") as f:
            cookies = json.load(f)
        print(f"✅ Loaded {len(cookies)} cookies (may help with access)")
    except:
        print("⚠️ No cookies file found, proceeding without cookies.")
        cookies = None
    
    # Configure browser
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=False,  # Set to True once you're confident it works
        cookies=cookies,
        verbose=True
    )
    
    # Configure crawl - focus on the target page directly
    crawl_config = CrawlerRunConfig(
        cache_mode="bypass",
        wait_until="networkidle",
        js_code="""
        // Simple scroll to try and load any lazy-loaded public content
        window.scrollBy(0, 500);
        await new Promise(r => setTimeout(r, 2000));
        window.scrollBy(0, 500);
        """,
        scan_full_page=True
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("\n🚀 Attempting to fetch the ODPC Kenya public page...")
        
        result = await crawler.arun(
            "https://www.facebook.com/ODPCKenya/",
            config=crawl_config
        )
        
        if result.success:
            print("✅ Page fetched successfully!")
            
            # Save the full HTML for inspection
            with open("odpckenya_public.html", "w", encoding="utf-8") as f:
                f.write(result.html)
            print("💾 Saved full page HTML to odpckenya_public.html")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # --- Try to extract public posts ---
            print("\n🔍 Attempting to extract public posts...")
            
            # Common containers for public posts (these vary, so we try several)
            possible_posts = []
            
            # Method 1: Look for elements with role="article" (common for posts)
            articles = soup.find_all('div', {'role': 'article'})
            if articles:
                possible_posts.extend(articles)
                print(f"📌 Found {len(articles)} elements with role='article'")
            
            # Method 2: Look for common post container classes (these change frequently)
            post_classes = ['userContent', '_5pcr', 'kvgmc6g5', 'cxmmr5t8', 'oygrvhab', 'hcukyx3x']
            for class_name in post_classes:
                elements = soup.find_all('div', {'class': re.compile(class_name)})
                if elements:
                    possible_posts.extend(elements)
                    print(f"📌 Found {len(elements)} elements with class containing '{class_name}'")
            
            # Method 3: Look for links that might be post permalinks
            post_links = soup.find_all('a', {'href': re.compile(r'/posts/|/photos/|/videos/')})
            if post_links:
                print(f"📌 Found {len(post_links)} potential post links")
            
            # Remove duplicates while preserving order
            seen = set()
            unique_posts = []
            for post in possible_posts:
                post_id = id(post)
                if post_id not in seen:
                    seen.add(post_id)
                    unique_posts.append(post)
            
            print(f"\n📊 Total unique potential post containers: {len(unique_posts)}")
            
            # Extract and save text from potential posts
            output_file = "odpckenya_public_posts.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("ODPC Kenya - Public Facebook Posts\n")
                f.write("=" * 60 + "\n\n")
                
                post_count = 0
                for i, post in enumerate(unique_posts[:50]):  # Check first 50
                    text = post.get_text(strip=True, separator='\n')
                    
                    # Clean up the text
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    clean_text = '\n'.join(lines)
                    
                    # Only save if it looks like substantive content (not just buttons/menus)
                    if clean_text and len(clean_text) > 100:  # Adjust threshold as needed
                        post_count += 1
                        f.write(f"POST #{post_count}\n")
                        f.write("-" * 40 + "\n")
                        f.write(clean_text)
                        f.write("\n\n" + "=" * 60 + "\n\n")
                
                if post_count > 0:
                    print(f"✅ Extracted {post_count} potential public posts to {output_file}")
                else:
                    print("⚠️ No substantial post text found. The public page may have very limited content.")
                    
                    # As a fallback, save any visible text from the main content area
                    body_text = soup.get_text()
                    with open("odpckenya_all_text.txt", "w", encoding="utf-8") as f2:
                        f2.write(body_text)
                    print("💾 Saved all page text to odpckenya_all_text.txt as fallback.")
            
        else:
            print(f"❌ Failed to fetch page: {result.error_message}")

async def main():
    await extract_public_facebook_content()
    print("\n✨ Done. Check the output files for any public posts.")

if __name__ == "__main__":
    asyncio.run(main())
