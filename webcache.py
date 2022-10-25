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
            return None

    async def get_text(self) -> str:
        return await self.page.inner_text("div[data-gramm_editor='false']")

    async def cut_paste(self) -> None:
        await self.page.keyboard.press("Control+A")
        await self.page.keyboard.press("Control+X")
        await self.page.keyboard.press("Control+V")


async def quilling(text) -> str:
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True, timeout=0)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto("https://quillbot.com/grammar-check", timeout=5000)
        except Exception:
            await page.reload()

        quillbot = QuillBot(page)

        # TODO: Make this dynamically recursive. Break on the fix_all_errors() timeout.
        await quillbot.type_text(text)
        await quillbot.fix_all_errors()
        text = await quillbot.get_text()
        await quillbot.cut_paste()
        await quillbot.fix_all_errors()
        text = await quillbot.get_text()
        await quillbot.cut_paste()
        await quillbot.fix_all_errors()
        return await quillbot.get_text()
