from pathlib import Path
from urllib.parse import quote_plus
import asyncio

import httpx

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from logger import logger
from read_file import read_file


ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "data" / "products"

AMAZON_BASE_URL = "https://www.amazon.com"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_product_urls(
    driver: webdriver.Chrome,
    keyword: str
) -> list[str]:

    search_url = f"{AMAZON_BASE_URL}/s?k={quote_plus(keyword)}"
    logger.info("Searching Amazon for keyword=%r", keyword)

    driver.get(AMAZON_BASE_URL)
    wait = WebDriverWait(driver, 10)    
    driver.get(search_url)
    wait = WebDriverWait(driver, 15)

    products = wait.until(
        EC.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                "div[data-component-type='s-search-result']"
            )
        )
    )

    product_urls = []
    skipped_products = 0
    for product in products:
        try:
            link = product.find_element(
                By.CSS_SELECTOR,
                "a[href*='/dp/'], a[href*='/gp/product/']"
            )
            url = link.get_attribute("href")
            if url and url not in product_urls:
                product_urls.append(url)

        except Exception:
            skipped_products += 1
            continue
    logger.info(
        "Found %d products for keyword=%r; skipped=%d",
        len(product_urls),
        keyword,
        skipped_products,
    )

    return product_urls


async def fetch_product(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
    keyword_index: int,
    product_index: int,
):
    async with semaphore:

        try:
            response = await client.get(url)
            logger.info(
                "[%d:%d] HTTP %d %s",
                keyword_index,
                product_index,
                response.status_code,
                url,
            )

            response.raise_for_status()
            html = response.text
            if "productTitle" not in html:
                logger.warning(
                    "[%d:%d] Unexpected HTML received from %s",
                    keyword_index,
                    product_index,
                    url,
                )
                return

            filename = (
                f"keyword_{keyword_index:02d}_"
                f"product_{product_index:03d}.html"
            )

            file_path = OUTPUT_DIR / filename

            file_path.write_text(
                html,
                encoding="utf-8"
            )

            logger.info(
                "[%d:%d] Saved %s",
                keyword_index,
                product_index,
                file_path,
            )

        except httpx.HTTPError as e:
            logger.error(
                "[%d:%d] HTTP error for %s: %s",
                keyword_index,
                product_index,
                url,
                e,
            )
        except OSError:
            logger.exception(
                "[%d:%d] Could not save product from %s",
                keyword_index,
                product_index,
                url,
            )


async def fetch_all_products(product_urls: list[tuple]):

    # Don't send hundreds/thousands of requests at once.
    semaphore = asyncio.Semaphore(5)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/152.0.7977.83 Safari/537.36"
        )
    }

    logger.info("Fetching %d product pages", len(product_urls))

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=20.0,
        headers=headers,
    ) as client:

        tasks = [
            fetch_product(
                client,
                semaphore,
                url,
                keyword_index,
                product_index,
            )
            for url, keyword_index, product_index
            in product_urls
        ]

        await asyncio.gather(*tasks)
    logger.info("Finished fetching product pages")


def scrape_keywords(keywords: list[str]):

    logger.info("Starting scrape for %d keywords", len(keywords))
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    all_product_urls = []

    try:
        for keyword_index, keyword in enumerate(
            keywords,
            start=1
        ):

            product_urls = get_product_urls(
                driver,
                keyword
            )

            for product_index, url in enumerate(
                product_urls,
                start=1
            ):

                all_product_urls.append(
                    (
                        url,
                        keyword_index,
                        product_index,
                    )
                )

    finally:

        driver.quit()
        logger.debug("Closed Chrome WebDriver")

    logger.info("Collected %d product URLs", len(all_product_urls))

    asyncio.run(
        fetch_all_products(all_product_urls)
    )

if __name__ == "__main__":
    df = read_file()
    keywords = df["Search Keywords"].dropna().tolist()
    logger.info("Loaded %d keywords from the input workbook", len(keywords))
    scrape_keywords(keywords)