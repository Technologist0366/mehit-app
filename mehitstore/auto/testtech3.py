#!/usr/bin/env python3
import asyncio
import json
import re
import os
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import html

class FacebookManualScraper:
    def __init__(self):
        self.output_dir = f"facebook_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def scrape_page(self, url):
        """Main scraping method"""
        print("=" * 70)
        print("📱 ODPC Kenya - Manual Facebook Scraper v2")
        print("=" * 70)
        
        # Load cookies
        try:
            with open("facebook_cookies_fixed.json", "r") as f:
                cookies = json.load(f)
            print(f"✅ Loaded {len(cookies)} cookies")
        except:
            print("⚠️ No cookies found")
            cookies = None
        
        # Browser config
        browser_config = BrowserConfig(
            browser_type="chromium",
            headless=False,  # Keep visible to see what happens
            cookies=cookies,
            verbose=True
        )
        
        # Crawl config with better scrolling
        crawl_config = CrawlerRunConfig(
            cache_mode="bypass",
            wait_until="networkidle",
            js_code=self.get_scroll_script(),
            scan_full_page=True
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            print("\n🌐 Fetching page with enhanced scrolling...")
            
            result = await crawler.arun(url, config=crawl_config)
            
            if result.success:
                print("✅ Page fetched successfully!")
                
                # Save raw HTML
                self.save_raw_html(result.html)
                
                # Parse and extract posts
                posts = self.extract_all_posts(result.html)
                
                if posts:
                    self.save_posts(posts)
                    self.print_summary(posts)
                else:
                    print("\n❌ No posts found with primary methods.")
                    print("🔍 Trying alternative extraction...")
                    
                    # Try alternative method - look for ANY content
                    self.extract_alternative_content(result.html)
            else:
                print(f"❌ Failed: {result.error_message}")
    
    def get_scroll_script(self):
        """JavaScript for better scrolling"""
        return """
        // Multiple scrolls to load content
        async function scroll() {
            let lastHeight = 0;
            let scrollCount = 0;
            const maxScrolls = 10;
            
            while (scrollCount < maxScrolls) {
                lastHeight = document.body.scrollHeight;
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(r => setTimeout(r, 3000));
                
                let newHeight = document.body.scrollHeight;
                if (newHeight === lastHeight) break;
                
                scrollCount++;
                console.log(`Scroll ${scrollCount} complete`);
            }
        }
        await scroll();
        """
    
    def extract_all_posts(self, html_content):
        """Multiple methods to find posts"""
        soup = BeautifulSoup(html_content, 'html.parser')
        posts = []
        
        print("\n🔍 Attempting multiple extraction methods:")
        
        # Method 1: Look for elements with role="article"
        articles = soup.find_all('div', {'role': 'article'})
        if articles:
            posts.extend(articles)
            print(f"✅ Method 1: Found {len(articles)} elements with role='article'")
        
        # Method 2: Look for common post containers from your manual output
        text_patterns = [
            'Following Kenya’s health financing',
            'Data Commissioner',
            'health financing agreement',
            '#DataPrivacyConference2026'
        ]
        
        for pattern in text_patterns:
            elements = soup.find_all(string=re.compile(pattern, re.I))
            for element in elements:
                parent = element.parent
                if parent and parent not in posts:
                    # Walk up to find post container
                    for _ in range(5):  # Go up 5 levels
                        if parent.get('role') == 'article' or 'post' in str(parent.get('class', '')):
                            posts.append(parent)
                            break
                        parent = parent.parent
                        if not parent:
                            break
            if elements:
                print(f"✅ Method 2: Found {len(elements)} elements with text pattern '{pattern}'")
        
        # Method 3: Look for any div with post-like attributes
        post_attributes = [
            {'data-testid': 'post_message'},
            {'data-ad-preview': 'message'},
            {'data-pagelet': 'ProfileTimeline'},
            {'class': re.compile(r'[a-zA-Z0-9]{15,}')}  # Facebook's hash classes
        ]
        
        for attrs in post_attributes:
            elements = soup.find_all('div', attrs)
            if elements:
                posts.extend(elements)
                print(f"✅ Method 3: Found {len(elements)} with {attrs}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_posts = []
        for post in posts:
            post_text = post.get_text(strip=True)
            if post_text and len(post_text) > 100 and post_text not in seen:
                seen.add(post_text)
                unique_posts.append(post)
        
        print(f"\n📊 Total unique posts after deduplication: {len(unique_posts)}")
        return unique_posts
    
    def extract_alternative_content(self, html_content):
        """When post detection fails, extract everything"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Get all text
        text = soup.get_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        # Save all text
        all_text_file = f"{self.output_dir}/all_text.txt"
        with open(all_text_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"\n💾 Saved all page text to {all_text_file}")
        
        # Look specifically for the post we know exists
        print("\n🔍 Searching for known post content:")
        known_phrases = [
            "Kenya's health financing agreement with the USA",
            "Data Commissioner",
            "#DataPrivacyConference2026",
            "@ikassait",
            "@ntvkenya"
        ]
        
        found_content = []
        for phrase in known_phrases:
            matches = [line for line in lines if phrase.lower() in line.lower()]
            if matches:
                found_content.extend(matches)
                print(f"✅ Found '{phrase[:50]}...'")
        
        if found_content:
            known_file = f"{self.output_dir}/known_content.txt"
            with open(known_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(found_content))
            print(f"💾 Saved known content to {known_file}")
    
    def save_raw_html(self, html_content):
        """Save raw HTML for debugging"""
        raw_file = f"{self.output_dir}/raw_page.html"
        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"💾 Saved raw HTML to {raw_file}")
    
    def save_posts(self, posts):
        """Save extracted posts with metadata"""
        posts_file = f"{self.output_dir}/extracted_posts.txt"
        json_file = f"{self.output_dir}/extracted_posts.json"
        
        posts_data = []
        
        with open(posts_file, 'w', encoding='utf-8') as f:
            f.write("ODPC KENYA - FACEBOOK POSTS\n")
            f.write(f"Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            
            for i, post in enumerate(posts, 1):
                # Get clean text
                text = post.get_text(strip=True, separator='\n')
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                clean_text = '\n'.join(lines)
                
                # Try to find date
                date = self.extract_date(post)
                
                # Look for images
                images = post.find_all('img')
                img_urls = [img.get('src', '') for img in images if img.get('src')]
                
                # Look for links
                links = post.find_all('a', href=True)
                external_links = [link['href'] for link in links 
                                if link['href'] and 'facebook.com' not in link['href']]
                
                # Save post
                f.write(f"POST #{i}\n")
                f.write(f"Date: {date}\n")
                f.write("-" * 40 + "\n")
                f.write(f"{clean_text}\n\n")
                
                if img_urls:
                    f.write(f"Images ({len(img_urls)}):\n")
                    for url in img_urls[:3]:
                        f.write(f"  • {url[:100]}...\n")
                    f.write("\n")
                
                if external_links:
                    f.write(f"Links ({len(external_links)}):\n")
                    for link in external_links[:3]:
                        f.write(f"  • {link[:100]}...\n")
                    f.write("\n")
                
                f.write("=" * 70 + "\n\n")
                
                # Save to JSON data
                posts_data.append({
                    'post_number': i,
                    'date': date,
                    'content': clean_text,
                    'images': img_urls,
                    'links': external_links
                })
        
        # Save JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved {len(posts)} posts to:")
        print(f"   - {posts_file}")
        print(f"   - {json_file}")
    
    def extract_date(self, post_element):
        """Extract post date using multiple methods"""
        # Look for time tags
        time_tag = post_element.find('time')
        if time_tag:
            return time_tag.get_text(strip=True)
        
        # Look for common date patterns
        date_patterns = [
            r'\d+\s+(hour|day|week|month|year)s?\s+ago',
            r'[A-Z][a-z]{2}\s+\d{1,2}(?:st|nd|rd|th)?',
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'Yesterday',
            r'Just now'
        ]
        
        text = post_element.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group()
        
        return "Date not found"
    
    def print_summary(self, posts):
        """Print summary of found posts"""
        print("\n" + "=" * 70)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 70)
        
        total_images = sum(len(post.find_all('img')) for post in posts)
        total_links = sum(len(post.find_all('a', href=True)) for post in posts)
        
        print(f"✅ Total posts found: {len(posts)}")
        print(f"🖼️  Total images found: {total_images}")
        print(f"🔗 Total links found: {total_links}")
        
        if posts:
            print("\n📝 First post preview:")
            first_post = posts[0].get_text(strip=True)[:300]
            print(f"{first_post}...")
        
        print(f"\n📁 All files saved to: {self.output_dir}/")

async def main():
    scraper = FacebookManualScraper()
    await scraper.scrape_page("https://www.facebook.com/ODPCKenya/")

if __name__ == "__main__":
    asyncio.run(main())
