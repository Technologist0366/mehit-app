#!/usr/bin/env python3
import asyncio
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig

async def test_facebook_login():
    print("=" * 60)
    print("🔐 Testing Facebook Login with Fixed Cookies")
    print("=" * 60)
    
    # Load the fixed cookies
    try:
        with open("facebook_cookies_fixed.json", "r") as f:
            cookies = json.load(f)
        print(f"✅ Loaded {len(cookies)} fixed cookies")
    except Exception as e:
        print(f"❌ Failed to load cookies: {e}")
        return False
    
    # Configure browser
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=False,  # Set to False so you can see what happens
        cookies=cookies,
        viewport_width=1280,
        viewport_height=720,
        verbose=True
    )
    
    # Simple crawl config
    crawl_config = CrawlerRunConfig(
        cache_mode="bypass",
        js_code="""
        // Wait for page to load
        await new Promise(r => setTimeout(r, 5000));
        
        // Check if we're logged in
        const isLoggedIn = !document.body.innerText.includes('登录');
        console.log('📱 Login status:', isLoggedIn ? '✅ LOGGED IN' : '❌ NEED LOGIN');
        
        // Take a mental note of the page title
        console.log('📄 Page title:', document.title);
        """,
        wait_until="networkidle"
    )
    
    print("\n🚀 Opening browser...")
    print("⏳ This will take 10-20 seconds...\n")
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        try:
            # Try to access Facebook
            result = await crawler.arun(
                "https://web.facebook.com/",
                config=crawl_config
            )
            
            if result.success:
                # Save the HTML for inspection
                with open("facebook_login_test.html", "w", encoding="utf-8") as f:
                    f.write(result.html)
                
                # Check if we're logged in
                html_lower = result.html.lower()
                if "login" not in html_lower and "登录" not in html_lower:
                    print("\n✅ SUCCESS! You are logged into Facebook!")
                    print("💾 Saved page HTML to: facebook_login_test.html")
                    
                    # Show a quick preview
                    soup = BeautifulSoup(result.html, 'html.parser')
                    title = soup.find('title')
                    if title:
                        print(f"📄 Page title: {title.text}")
                    
                    return True
                else:
                    print("\n❌ FAILED: Still on login page")
                    print("💾 Saved login page to: facebook_login_test.html")
                    print("\n🔍 Debug info:")
                    print("   - The page still shows a login form")
                    print("   - Cookies may be expired or invalid for this session")
                    return False
            else:
                print(f"\n❌ Failed to load page: {result.error_message}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False

async def main():
    success = await test_facebook_login()
    if success:
        print("\n🎉 Ready to run the full scraper!")
        print("   Now use facebook_cookies_fixed.json in your main script")
    else:
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure you're logged into Facebook in Chrome")
        print("   2. Export fresh cookies using EditThisCookie")
        print("   3. Run fix_cookies.py on the new export")
        print("   4. Try this test again")

if __name__ == "__main__":
    asyncio.run(main())
