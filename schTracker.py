from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import telegram
import schedule
import asyncio
from selenium.common.exceptions import ElementNotInteractableException

# Setup
driver_path = "C:/WebDriver/msedgedriver.exe"  # Update this to your actual path
product_url = "https://shop.amul.com/en/product/amul-whey-protein-32-g-or-pack-of-60-sachets"
pincode = "411033"
BOT_TOKEN = "YOUR_BOT_TOKEN" 
CHAT_ID = "YOUR_CHAT_ID"  # Replace with your chat ID. You will need to find this.


# Function to send Telegram message
async def send_telegram_message(message):
    """
    Sends a message to a Telegram chat. It is crucial to use async.
    """
    bot = telegram.Bot(token=BOT_TOKEN)
    async with bot:
        try:
            await bot.send_message(chat_id=CHAT_ID, text=message)
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")

async def check_stock():
    """
    Navigates to the product page, checks the stock status, and sends a Telegram message.
    """
    # Headless Edge options
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Start browser
    driver = webdriver.Edge(service=Service(driver_path), options=options)
    try:
        driver.get(product_url)
        wait = WebDriverWait(driver, 20)  

        # Wait and type pincode
        pincode_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='search' and @placeholder='Enter Your Pincode']")))
        try:
            pincode_input.send_keys(pincode)
        except ElementNotInteractableException:
            time.sleep(1)
            pincode_input.send_keys(pincode)

        # Wait for the dropdown suggestion to appear and click it
        suggestion = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@role='button']//p[text()='411033']")))
        try:
            suggestion.click()
        except ElementNotInteractableException:
            time.sleep(1)
            suggestion.click()

        # Wait for page content to reload (adjust if necessary)
        time.sleep(4)

        # Get full page source and search for stock info
        page = driver.page_source
        if "Sold Out" in page:
            await send_telegram_message("🔴 Out of Stock!")
        else:
            await send_telegram_message("🟢 Amul whey protein(unflavoured) pack of 60 is IN STOCK!")

    except Exception as e:
        error_message = f"❌ Error: {e}"
        print(error_message)
        await send_telegram_message(error_message)

    finally:
        driver.quit()

def run_threaded(job_func):
    """Runs an async job function in a separate thread."""
    import threading
    import asyncio

    def wrapper():
        asyncio.run(job_func())

    job_thread = threading.Thread(target=wrapper)
    job_thread.start()

if __name__ == "__main__":
    schedule.every().hour.do(run_threaded, check_stock)  # Run every minute for testing

    while True:
        schedule.run_pending()
        time.sleep(1)