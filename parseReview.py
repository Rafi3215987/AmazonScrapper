from bs4 import BeautifulSoup
from langdetect import detect
from deep_translator import GoogleTranslator

from logger import logger

def parseReview(productID: str) -> list:
    with open(
        f"data/products/{productID}",
        encoding="utf-8"
    ) as file:
        reviews = BeautifulSoup(file, "html.parser")
    review_data = []
    reviews = reviews.select(
         "div[data-hook='reviewRichContentContainer']"
    )

    #count = 0;
    for review in reviews:
        # count += 1
        # print(count)
        # print(review.get_text(strip = True))
        # print("\n")
        review = review.get_text(strip = True)
        try:
            language = detect(review)
        except Exception as e:
            logger.info("Language detection failed for review: %s", review)
            continue
        
        if language == "en":
            review_data.append({"review": review})
        else:
            try:
                translated_review = GoogleTranslator(source=language, target="en").translate(review)
                review_data.append({"review": translated_review})
            except Exception as e:
                logger.info("Translation failed for review: %s", review)
                continue

        

    return review_data
