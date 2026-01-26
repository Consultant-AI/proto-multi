#!/usr/bin/env python3
"""Convert HTML/CSS logos to PNG images."""

import asyncio
from pathlib import Path

async def convert_logos():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Error: playwright not installed")
        print("Run: pip install playwright && playwright install")
        return False

    script_dir = Path(__file__).parent
    html_file = script_dir / 'logos.html'

    print("Converting logos to PNG images...")

    logos = [
        ('wordmark-blue', 'proto_wordmark_blue_transparent.png'),
        ('wordmark-white', 'proto_wordmark_white_black.png'),
        ('wordmark-blue-white', 'proto_wordmark_blue_white.png'),
        ('icon-blue', 'proto_icon_blue_transparent.png'),
        ('icon-white', 'proto_icon_white_black.png'),
        ('icon-blue-white', 'proto_icon_blue_white.png'),
        ('lockup-blue', 'proto_lockup_blue_transparent.png'),
        ('lockup-white', 'proto_lockup_white_black.png'),
        ('favicon', 'favicon.png'),
        ('email-signature', 'proto_email_signature.png'),
        ('social-card', 'proto_social_card.png'),
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f'file://{html_file.absolute()}')
        await page.wait_for_timeout(2000)

        for element_id, filename in logos:
            element = page.locator(f'#{element_id}')
            output_path = script_dir / filename
            await element.screenshot(path=str(output_path))
            print(f"✓ {filename}")

        await browser.close()

    print(f"\nAll logos generated in: {script_dir}")
    return True

if __name__ == '__main__':
    asyncio.run(convert_logos())
