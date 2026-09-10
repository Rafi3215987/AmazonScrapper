from bs4 import BeautifulSoup
from logger import logger
from read_file import read_file

search_keywords = read_file()["Search Keywords"].tolist()

def get_text_or_none(product_page: BeautifulSoup, selector: str):
    element = product_page.select_one(selector)
    return element.get_text(strip=True) if element else None


def parsePriceRelatedFeatures(productID: str) -> dict:
    with open(
            f"data/products/{productID}",
            encoding ="utf-8"
        ) as file:
            productPage = BeautifulSoup(file, "html.parser")

    title = get_text_or_none(productPage, "span#productTitle")
    rating = get_text_or_none(productPage, "span#acrPopover")
    if rating:
        rating = rating[:3]
    ratingCount = get_text_or_none(productPage, "span#acrCustomerReviewText")
    
    description = get_text_or_none(productPage, "div#feature-bullets")
    category_index = int(productID[8:10]) - 1
    category = search_keywords[category_index] if category_index < len(search_keywords) else None

    price = get_text_or_none(productPage, "span#apex-pricetopay-accessibility-label")

    brandName = None
    for row in productPage.select("table tr"):
        label = row.find("span", class_="a-text-bold")
    
        if label and label.get_text(strip=True) == "Brand":
            value = row.find_all("td")[1]
            brand = value.get_text(strip=True)
            brandName = brand
            break

    print(f"Product ID: {productID}")
    if brandName is None:
        for row in productPage.select("table.prodDetTable tr"):
            key = row.find("th")
    
            if key and key.get_text(strip=True) == "Brand":
                value = row.find("td")
                if value:
                    brandName = value.get_text(strip=True)
                break

    print(brandName)

    product = {
        "category": category,
        "title": title,
        "brand": brandName,
        "rating": rating,
        "ratingCount": ratingCount,
        "description": description,
        "price": price
    }
    return product

if __name__ == "__main__":
    parsePriceRelatedFeatures("keyword_28_product_048.html")