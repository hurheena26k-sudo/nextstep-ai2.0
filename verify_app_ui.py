import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 950})
        await page.goto("http://localhost:8501", timeout=60000)
        await asyncio.sleep(4)
        await page.screenshot(path="/tmp/nextstep_chat_ui_final.png", full_page=True)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
