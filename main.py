from urllib.parse import quote_plus
import pandas as pd
import time
from parseReview import parseReview
from bs4 import BeautifulSoup
from read_file import read_file
from pathlib import Path
import json

def extract_reviews():
    #FEATURE B
    review_data = []
    products_dir = Path("data/products")
    for html in products_dir.glob("*.html"):
        filename: str = str(html.name)
        reviews = parseReview(filename)
        productName = BeautifulSoup(open(html, encoding="utf-8"), "html.parser").select_one("span#productTitle").get_text(strip=True)
        print(productName)
            
        data = {
            "productName": productName,
            "reviews": json.dumps(reviews, ensure_ascii=False, indent=4)
        }
        
        review_data.append(data)

    df = pd.DataFrame(review_data)
    df.to_csv("data/reviews.csv", index=False, encoding="utf-8-sig")




def main():
    #FEATURE A
    #FEATURE B
    extract_reviews()
    

#     df = read_file();
#     for indx, row in df.iterrows():
#         keyword = row["Search Keywords"]
# keyword = "gaming mouse"
# URL = f"https://www.amazon.com/s?k={quote_plus(keyword)}"
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
# driver = webdriver.Chrome()
# driver.get("https://www.amazon.com")
# wait = WebDriverWait(driver, 10)
# driver.get(URL)
# wait = WebDriverWait(driver, 10)

if __name__ == "__main__":
    main()
