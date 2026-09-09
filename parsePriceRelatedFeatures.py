from bs4 import BeautifulSoup
from logger import logger
from read_file import read_file

search_keywords = read_file()["Search Keywords"].tolist()

def parsePriceRelatedFeatures(productID: str) -> dict:
    with open(
            f"data/products/{productID}",
            encoding ="utf-8"
        ) as file:
            productPage = BeautifulSoup(file, "html.parser")

    title = productPage.select_one("span#productTitle").get_text(strip=True)
    rating = productPage.select_one("span#acrPopover").get_text(strip=True)[:3]
    ratingCount = productPage.select_one("span#acrCustomerReviewText").get_text(strip=True)
    brandName = None
    description = productPage.select_one("div#feature-bullets").get_text(strip=True)
    print(int(productID[8:10]))
    category = search_keywords[int(productID[8:10])-1]

    for row in productPage.select("table.prodDetTable tr"):
        key = row.find("th")

        if key and key.get_text(strip=True) == "Brand":
            value = row.find("td")
            if value:
                brandName = value.get_text(strip=True)
            break

    #print(brandName)

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