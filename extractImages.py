from bs4 import BeautifulSoup
import httpx
from pathlib import Path


def downloadImage(
        URL : str,
        output_path : str
) -> bool:
    try:
        response = httpx.get(
            URL,
            timeout = 30
        )
        response.raise_for_status()

        with open(
            output_path,
            "wb"
        )as file:
            file.write(response.content)

        return True

    except httpx.HTTPError as error:
        print(f"Failed to download image: {error}")
        return False


def extractImages(productID: str):
    with open(
        f"data/products/{productID}",
        encoding="utf-8"
    ) as file:
        soup = BeautifulSoup(file, "html.parser")

    img = soup.select_one(
        "div[class='imgTagWrapper'] img[id='landingImage']"
    )

    img_url = img.get("src")
    dir = Path("data/images")
    dir.mkdir(parents=True, exist_ok=True)
    output_file = dir / f"{productID.replace('.html', '')}.jpg"
    downloadImage(img_url, str(output_file)) 
        



if __name__ == "__main__":
    extractImages("keyword_28_product_001.html")

