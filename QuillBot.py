from playwright.async_api import async_playwright


class QuillBot:
    def __init__(self, page) -> None:
        self.page = page

    async def type_text(self, text: str) -> None:
        await self.page.click("div[data-gramm_editor='false']")
        await self.page.keyboard.type(text)

    async def fix_all_errors(self) -> None:
        try:
            await self.page.click("text=Fix All Errors", timeout=1500)
            await self.page.wait_for_selector("text=Fixed all grammar errors.")
        except Exception:
            return None

    async def get_text(self) -> str:
        return await self.page.inner_text("div[data-gramm_editor='false']")

    async def cut_paste(self) -> None:
        await self.page.keyboard.press("Control+A")
        await self.page.keyboard.press("Control+X")
        await self.page.keyboard.press("Control+V")

    # TODO: Find correct HTML to close Google Sign In -> Firefox
    # OUTER HTML:
    # <div id="close" class="TvD9Pc-Bz112c ZYIfFd-aGxpHf-FnSee" role="button" aria-label="Close" tabindex="0"><div class="Bz112c-ZmdkE"></div><svg class="Bz112c Bz112c-r9oPif" xmlns="https://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#5f6368"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"></path><path fill="none" d="M0 0h24v24H0z"></path></svg></div>

    # INNER HTML:
    # <div class="Bz112c-ZmdkE"></div><svg class="Bz112c Bz112c-r9oPif" xmlns="https://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#5f6368"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"></path><path fill="none" d="M0 0h24v24H0z"></path></svg>

    # XPATH:
    # //*[@id="close"]

    async def close_signin(self) -> None:
        # Click the close button based on the above HTML
        try:
            await self.page.click("div#close")
        except Exception:
            return None


async def recursive_quilling(
    initial_text: str, quillbot: QuillBot, iteration_count: int = 0
) -> str:
    await quillbot.fix_all_errors()
    text = await quillbot.get_text()
    if text == initial_text:
        return text
    await quillbot.page.wait_for_timeout(50)
    await quillbot.cut_paste()
    return await recursive_quilling(text, quillbot, iteration_count)


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

        # await quillbot.close_signin()
        await quillbot.type_text(text)
        return await recursive_quilling(text, quillbot)
