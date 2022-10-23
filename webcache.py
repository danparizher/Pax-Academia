from playwright.sync_api import sync_playwright


class QuillBot:
    def __init__(self, page) -> None:
        self.page = page

    def type_text(self) -> None:
        self.page.click("div[data-gramm_editor='false']")
        self.page.keyboard.type(input("Enter text: "))

    def fix_all_errors(self) -> None:
        try:
            self.page.click("text=Fix All Errors", timeout=5000)
            self.page.wait_for_selector("text=Fixed all grammar errors.")
        except Exception:
            print("No errors found")
            exit()

    def get_text(self) -> str:
        return self.page.inner_text("div[data-gramm_editor='false']")


def main() -> None:
    with sync_playwright() as p:
        with p.firefox.launch(headless=True, timeout=0) as browser:
            context = browser.new_context()
            page = context.new_page()

            try:
                page.goto("https://quillbot.com/grammar-check", timeout=5000)
            except Exception:
                page.reload()

            quillbot = QuillBot(page)

            quillbot.type_text()
            quillbot.fix_all_errors()

            print("\nCorrected text:", quillbot.get_text())
