#!/usr/bin/env python3
import asyncio
import json
import re
import requests
import os
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse

async def extract_facebook_with_media():
    print("=" * 70)
    print("📱 ODPC Kenya - Complete Content Extractor (Posts + Media)")
    print("=" * 70)
    
    # Load cookies
    cookies = None
    try:
        with open("facebook_cookies_fixed.json", "r") as f:
            cookies = json.load(f)
        print(f"✅ Loaded {len(cookies)} cookies")
    except:
        print("⚠️ No cookies found")
    
    # Configure browser
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        cookies=cookies,
        verbose=False
    )
    
    crawl_config = CrawlerRunConfig(
        cache_mode="bypass",
        wait_until="domcontentloaded",
        page_timeout=30000,
        js_code="""
        // Scroll to load images
        window.scrollBy(0, 300);
        await new Promise(r => setTimeout(r, 1000));
        window.scrollBy(0, 300);
        await new Promise(r => setTimeout(r, 1000));
        window.scrollTo(0, document.body.scrollHeight);
        """
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("\n🌐 Fetching page with media content...")
        
        result = await crawler.arun(
            "https://www.facebook.com/ODPCKenya/",
            config=crawl_config
        )
        
        if result.success:
            print("✅ Page fetched successfully!")
            
            # Create output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"odpckenya_content_{timestamp}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save HTML
            html_file = f"{output_dir}/page.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(result.html)
            print(f"💾 Saved HTML to {html_file}")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Create main content file
            content_file = f"{output_dir}/all_content.txt"
            
            with open(content_file, "w", encoding="utf-8") as f:
                f.write("ODPC KENYA - FACEBOOK CONTENT\n")
                f.write("=" * 70 + "\n")
                f.write(f"Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 70 + "\n\n")
                
                # =============================================
                # 1. PAGE INFORMATION
                # =============================================
                f.write("📊 PAGE INFORMATION\n")
                f.write("-" * 40 + "\n")
                
                # Page name
                page_name = soup.find('title')
                if page_name:
                    f.write(f"Title: {page_name.text}\n")
                
                # Follower count
                followers = soup.find(string=re.compile(r'[\d.,]+\s*follower', re.I))
                if followers:
                    f.write(f"Followers: {followers}\n")
                
                # About text
                about = soup.find(string=re.compile(r'Public and government service|Data Protection', re.I))
                if about:
                    parent = about.parent
                    if parent:
                        f.write(f"About: {parent.get_text(strip=True)[:200]}...\n")
                
                f.write("\n" + "=" * 70 + "\n\n")
                
                # =============================================
                # 2. POSTS WITH FULL CONTENT
                # =============================================
                f.write("📝 POSTS\n")
                f.write("=" * 70 + "\n\n")
                
                # Find all potential posts
                posts = []
                posts.extend(soup.find_all('div', {'role': 'article'}))
                posts.extend(soup.find_all('div', {'class': re.compile(r'userContent|post|story', re.I)}))
                
                # Remove duplicates
                seen = set()
                unique_posts = []
                for post in posts:
                    post_text = post.get_text(strip=True)
                    if post_text and len(post_text) > 50 and post_text not in seen:
                        seen.add(post_text)
                        unique_posts.append(post)
                
                print(f"\n📊 Found {len(unique_posts)} unique posts")
                
                # Process each post
                for post_idx, post in enumerate(unique_posts[:20], 1):
                    f.write(f"\n{'='*60}\n")
                    f.write(f"POST #{post_idx}\n")
                    f.write(f"{'='*60}\n\n")
                    
                    # Post text
                    text = post.get_text(strip=True, separator='\n')
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    clean_text = '\n'.join(lines)
                    f.write(f"{clean_text}\n\n")
                    
                    # =========================================
                    # 2a. IMAGES in this post
                    # =========================================
                    images = post.find_all('img')
                    if images:
                        f.write("📷 IMAGES:\n")
                        f.write("-" * 30 + "\n")
                        
                        for img_idx, img in enumerate(images[:5]):  # Max 5 images per post
                            img_url = img.get('src', '')
                            if img_url and not img_url.startswith('data:'):
                                # Make URL absolute
                                if img_url.startswith('/'):
                                    img_url = 'https://www.facebook.com' + img_url
                                
                                alt_text = img.get('alt', 'No description')
                                f.write(f"\nImage {img_idx+1}:\n")
                                f.write(f"  URL: {img_url[:100]}...\n")
                                f.write(f"  Alt: {alt_text[:100]}\n")
                                
                                # Try to download image
                                try:
                                    img_data = requests.get(img_url, timeout=5).content
                                    img_file = f"{output_dir}/post{post_idx}_img{img_idx+1}.jpg"
                                    with open(img_file, 'wb') as img_f:
                                        img_f.write(img_data)
                                    print(f"  💾 Downloaded image {img_idx+1} for post {post_idx}")
                                except:
                                    pass
                        f.write("\n")
                    
                    # =========================================
                    # 2b. VIDEOS in this post
                    # =========================================
                    videos = post.find_all(['video', 'div'], {'class': re.compile(r'video', re.I)})
                    video_links = post.find_all('a', {'href': re.compile(r'/videos/|watch', re.I)})
                    
                    if videos or video_links:
                        f.write("🎥 VIDEOS:\n")
                        f.write("-" * 30 + "\n")
                        
                        for vid in videos[:3]:
                            f.write(f"  • Video element found\n")
                        
                        for link in video_links[:3]:
                            href = link.get('href', '')
                            if href:
                                f.write(f"  • Video link: {href[:100]}...\n")
                        f.write("\n")
                    
                    # =========================================
                    # 2c. LINKS in this post
                    # =========================================
                    links = post.find_all('a', href=True)
                    external_links = []
                    for link in links:
                        href = link.get('href', '')
                        if href and not href.startswith('/') and 'facebook.com' not in href:
                            external_links.append(href)
                    
                    if external_links:
                        f.write("🔗 EXTERNAL LINKS:\n")
                        f.write("-" * 30 + "\n")
                        for link in external_links[:3]:
                            f.write(f"  • {link[:100]}...\n")
                        f.write("\n")
                    
                    # =========================================
                    # 2d. REACTIONS & COMMENTS
                    # =========================================
                    reactions = post.find_all(string=re.compile(r'reactions?|like|comment|share', re.I))
                    reaction_text = ' '.join([str(r) for r in reactions[:5]])
                    if reaction_text:
                        f.write("💬 ENGAGEMENT:\n")
                        f.write("-" * 30 + "\n")
                        f.write(f"{reaction_text}\n\n")
                    
                    f.write("\n")
                
                # =============================================
                # 3. ALL MEDIA SUMMARY
                # =============================================
                f.write("\n" + "=" * 70 + "\n")
                f.write("📊 MEDIA SUMMARY\n")
                f.write("=" * 70 + "\n\n")
                
                # Count all images
                all_images = soup.find_all('img')
                unique_images = set()
                for img in all_images:
                    src = img.get('src', '')
                    if src and not src.startswith('data:'):
                        unique_images.add(src[:200])
                
                f.write(f"Total unique images found: {len(unique_images)}\n")
                
                # Count all videos
                all_videos = soup.find_all(['video', 'div'], {'class': re.compile(r'video', re.I)})
                f.write(f"Video elements found: {len(all_videos)}\n")
                
                # Save image URLs separately
                img_file = f"{output_dir}/all_image_urls.txt"
                with open(img_file, "w") as img_f:
                    for img_url in unique_images:
                        img_f.write(f"{img_url}\n")
                print(f"💾 Saved image URLs to {img_file}")
            
            print(f"\n✅ All content saved to directory: {output_dir}/")
            print(f"   Main content file: all_content.txt")
            print(f"   Image URLs: all_image_urls.txt")
            
            # Show preview of what we found
            print("\n📋 Preview of extracted content:")
            print("-" * 40)
            with open(content_file, "r") as f:
                preview = f.read()[:1000] + "..."
                print(preview)
            
        else:
            print(f"❌ Failed: {result.error_message}")

async def main():
    await extract_facebook_with_media()

if __name__ == "__main__":
    asyncio.run(main())
