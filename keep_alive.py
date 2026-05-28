"""Keep Streamlit apps alive with headless Selenium."""

from __future__ import annotations

import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


TARGET_URLS = [
    "https://goodluke.streamlit.app/",
    "https://civitas-radar.streamlit.app/",
]
WAIT_SECONDS = 15
WAKE_TIMEOUT = 30
SCREENSHOT_PATH = "keep_alive_screenshot.png"


def build_driver() -> webdriver.Chrome:
    options = Options()
    # "--headless=new" evita o modo legada e melhora estabilidade em runners atuais.
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")

    return webdriver.Chrome(options=options)


def wake_up_app(driver: webdriver.Chrome, url: str) -> None:
    """Visit the URL and click the Streamlit wake-up button if the app is sleeping."""
    print(f"Visiting: {url}")
    driver.set_page_load_timeout(60)
    driver.get(url)
    time.sleep(WAIT_SECONDS)

    # Streamlit shows a wake-up button when the app is sleeping.
    # The button text is typically "Yes, get this app back up!"
    try:
        wake_button = WebDriverWait(driver, WAKE_TIMEOUT).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(), 'Yes, get this app back up')]")
            )
        )
        wake_button.click()
        print(f"  Wake-up button clicked for {url}. Waiting for app to start…")
        time.sleep(WAIT_SECONDS * 2)
    except Exception:
        # Button not found – app is already awake
        print(f"  App appears to be awake already: {url}")

    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    app_name = url.split("//")[1].split(".")[0]
    screenshot_file = SCREENSHOT_PATH.replace(".png", f"-{app_name}-{timestamp}.png")
    driver.save_screenshot(screenshot_file)
    print(f"  Screenshot saved: {screenshot_file}")


def run() -> None:
    driver: webdriver.Chrome | None = None
    try:
        driver = build_driver()
        for url in TARGET_URLS:
            try:
                wake_up_app(driver, url)
            except Exception as exc:
                print(f"Keep-alive failed for {url}: {exc}")
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    run()
