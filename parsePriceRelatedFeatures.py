from bs4 import BeautifulSoup
from logger import logger

def parsePriceRelatedFeatures(productID: str) -> dict:
    with open(
            f"data/products/{productID}",
            encoding ="utf-8"
        ) as file:
            productPage = BeautifulSoup(file, "html.parser")

    title = productPage.select_one("span#productTitle").get_text(strip=True)
    rating = productPage.select_one("span#acrPopover").get_text(strip=True)[:3]
    ratingCount = productPage.select_one("span#acrCustomerReviewText").get_text(strip=True)
    brandName = productPage.select_one("tr.po-brand span.a-size-base.po-break-word").get_text(strip=True)
    description = productPage.select_one("div#feature-bullets").get_text(strip=True)
    category = productPage.select_one("a[aria-current='page']").get_text(strip=True)

    product = {
        "category": category,
        "title": title,
        "brand": brandName,
        "rating": rating,
        "ratingCount": ratingCount,
        "description": description
    }
    print(product)
    return product

if __name__ == "__main__":
    parsePriceRelatedFeatures("keyword_04_product_008.html")