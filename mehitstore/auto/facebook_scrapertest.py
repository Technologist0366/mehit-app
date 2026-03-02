#!/usr/bin/env python3
import asyncio
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig

async def test_login():
    # Load cookies
    with open("facebook_cookies.json", "r") as f:
        cookies = json.load(f)
    
    print(f"Testing with {len(cookies)} cookies...")
    
    # Browser with cookies
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=False,
        cookies=cookies
    )
    
    # Simple crawl config
    crawl_config = CrawlerRunConfig(
        cache_mode="bypass",
        js_code="console.log('Testing login...')"
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            "https://web.facebook.com/",
            config=crawl_config
        )
        
        if result.success:
            if "login" not in result.html.lower():
                print("✅ LOGIN WORKING!")
                with open("login_test.html", "w") as f:
                    f.write(result.html)
            else:
                print("❌ Login failed")

asyncio.run(test_login())
