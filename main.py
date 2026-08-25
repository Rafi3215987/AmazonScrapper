import pandas as pd
from urllib.parse import quote_plus
from selenium import webdriver
import pandas as pd

keyword = "gaming mouse"
URL = f"https://www.amazon.com/s?k={quote_plus(keyword)}"

print(URL)

driver = webdriver.Chrome()
print(driver.get(URL))
