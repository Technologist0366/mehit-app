#!/usr/bin/env python3
import asyncio
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig

async def minimal_test():
    print("=" * 60)
    print("🔧 Minimal Facebook Test")
    print("=" * 60)
    
    # Load your fixed cookies
    with open("facebook_cookies_fixed.json", "r") as f:
        cookies = json.load(f)
    print(f"✅ Loaded {len(cookies)} cookies")
    
    # Minimal browser config
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=False,
        cookies=cookies,
        verbose=True
    )
    
    # Minimal crawl config - NO JavaScript execution
    crawl_config = CrawlerRunConfig(
        cache_mode="bypass",
        wait_until="domcontentloaded",  # Faster, less detection
        scan_full_page=False
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("\n🚀 Opening browser (watch what happens)...")
        
        result = await crawler.arun(
            "https://www.facebook.com/",  # Try www subdomain
            config=crawl_config
        )
        
        if result.success:
            # Save the page
            with open("facebook_result.html", "w", encoding="utf-8") as f:
                f.write(result.html)
            print("💾 Saved page HTML to facebook_result.html")
            
            # Quick check
            if "login" not in result.html.lower():
                print("✅ SUCCESS! You're logged in!")
                # Now try the target page
                result2 = await crawler.arun(
                    "https://www.facebook.com/ODPCKenya/",
                    config=crawl_config
                )
                if result2.success:
                    with open("odpckenya_page.html", "w", encoding="utf-8") as f:
                        f.write(result2.html)
                    print("✅ Got ODPCKenya page!")
            else:
                print("❌ Still on login page")
        else:
            print(f"❌ Error: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(minimal_test())
