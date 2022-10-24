from playwright.async_api import async_playwright


class QuillBot:
    def __init__(self, page) -> None:
        self.page = page

    async def type_text(self, text: str) -> None:
        await self.page.click("div[data-gramm_editor='false']")
        await self.page.keyboard.type(text)

    async def fix_all_errors(self) -> None:
        try:
            await self.page.click("text=Fix All Errors", timeout=5000)
            await self.page.wait_for_selector("text=Fixed all grammar errors.")
        except Exception:
            print("No errors found")
            exit()

    async def get_text(self) -> str:
        return await self.page.inner_text("div[data-gramm_editor='false']")


# TODO: Input should be coming from user, not hardcoded (logic in bot.py)
async def quilling(text: str) -> str:
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True, timeout=0)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto("https://quillbot.com/grammar-check", timeout=5000)
        except Exception:
            await page.reload()

        quillbot = QuillBot(page)

        await quillbot.type_text(text)
        await quillbot.fix_all_errors()
        return await quillbot.get_text()
