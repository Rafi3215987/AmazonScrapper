from urllib.parse import quote_plus
import pandas as pd
from selenium import webdriver 
import time
#from selenium.webdriver.chrome.options import Options

keyword = "gaming mouse"
URL = f"https://www.amazon.com/s?k={quote_plus(keyword)}"

# UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/151.0.0.0 Safari/537.36")  

# options = Options()
# options.add_argument(f"user-agent={UA}")
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option("useAutomationExtension", False)
# options.add_argument("--start-maximized")
# options.add_argument("--lang=en-US,en")

# driver = webdriver.Chrome(options=options)

# driver.execute_cdp_cmd(
#     "Page.addScriptToEvaluateOnNewDocument",
#     {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"},
# )
driver = webdriver.Chrome()
driver.get("https://www.amazon.com")
time.sleep(5)
driver.get(URL)
time.sleep(120)
