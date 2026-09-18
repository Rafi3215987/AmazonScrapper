from pathlib import Path
import re

import pandas as pd
import streamlit as st
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
IMAGE_DIR = DATA_DIR / "images"

st.set_page_config(
    page_title="Amazon Feature Lab",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data

def load_similarity_data():
    path = DATA_DIR / "similarityRelatedFeatures.csv"
    frame = pd.read_csv(path)
    for column in ["category", "brand", "description", "title"]:
        frame[column] = frame[column].fillna("").astype(str)
    frame["price_value"] = frame["price"].str.extract(r"\$([\d,]+(?:\.\d+)?)")[0]
    frame["price_value"] = pd.to_numeric(
        frame["price_value"].str.replace(",", "", regex=False),
        errors="coerce",
    )
    frame["search_text"] = (
        frame["title"] + " " + frame["description"] + " " + frame["brand"]
    )
    return frame


@st.cache_data

def load_price_data():
    frame = pd.read_csv(DATA_DIR / "priceRelatedFeatures.csv")
    frame["price_value"] = frame["price"].astype(str).str.extract(
        r"\$([\d,]+(?:\.\d+)?)"
    )[0]
    frame["price_value"] = pd.to_numeric(
        frame["price_value"].str.replace(",", "", regex=False),
        errors="coerce",
    )
    frame["rating"] = pd.to_numeric(frame["rating"], errors="coerce")
    frame["rating_count"] = pd.to_numeric(
        frame["ratingCount"].astype(str).str.replace(",", "", regex=False).str.extract(
            r"(\d+(?:\.\d+)?)"
        )[0],
        errors="coerce",
    )
    frame = frame.dropna(subset=["price_value"]).drop_duplicates().copy()
    frame["price_percentile"] = frame.groupby("category")["price_value"].rank(
        pct=True, method="average"
    )
    frame["price_tier"] = pd.cut(
        frame["price_percentile"],
        bins=[0, 0.33, 0.67, 1.0],
        labels=["Budget", "Mid-range", "Premium"],
        include_lowest=True,
    )
    return frame


@st.cache_data

def load_reviews():
    path = DATA_DIR / "reviews.csv"
    raw = pd.read_csv(path)
    labeled_path = ROOT / "artifacts" / "feature_b" / "flattened_reviews_labeled.csv"
    if labeled_path.exists():
        reviews = pd.read_csv(labeled_path)
    else:
        reviews = raw.copy()
        reviews["sentiment"] = "unknown"
    for column in ["category", "productName", "review", "sentiment"]:
        if column not in reviews:
            reviews[column] = ""
        reviews[column] = reviews[column].fillna("").astype(str)
    return raw, reviews


@st.cache_data

def load_images():
    extensions = {".jpg", ".jpeg", ".png", ".webp"}
    records = []
    pattern = re.compile(
        r"^(?P<keyword>.+?)_(?P<product>product_\d+)\.(?P<extension>jpg|jpeg|png|webp)$",
        re.IGNORECASE,
    )
    for path in sorted(IMAGE_DIR.glob("*")):
        if path.suffix.lower() not in extensions:
            continue
        match = pattern.match(path.name)
        records.append(
            {
                "path": path,
                "filename": path.name,
                "keyword": match.group("keyword") if match else "unknown",
                "product": match.group("product") if match else "unknown",
            }
        )
    return pd.DataFrame(records)


def show_header():
    st.title("Amazon Feature Lab")
    st.caption("Explore product similarity, review sentiment, visual assets, and pricing patterns from the scraped catalog.")


def feature_a(frame):
    st.subheader("Feature A: Similar products")
    st.write("Search the product catalog with title, description, brand, and category-aware TF-IDF similarity.")
    query = st.text_input("Product or use-case", "wireless headphones", key="feature_a_query")
    category = st.selectbox(
        "Category filter",
        ["All categories"] + sorted(frame["category"].replace("", "Unknown").unique()),
        key="feature_a_category",
    )
    result_count = st.slider("Results", 5, 20, 10, key="feature_a_count")

    candidates = frame if category == "All categories" else frame[frame["category"] == category]
    if candidates.empty:
        st.info("No products match that category.")
        return
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=8000)
    matrix = vectorizer.fit_transform(candidates["search_text"])
    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, matrix).ravel()
    results = candidates.copy()
    results["similarity"] = scores
    results = results.sort_values("similarity", ascending=False).head(result_count)
    results["price"] = results["price_value"].map(lambda value: f"${value:,.2f}" if pd.notna(value) else "n/a")
    st.dataframe(
        results[["title", "brand", "category", "price", "similarity"]].rename(
            columns={"similarity": "match score"}
        ),
        use_container_width=True,
        hide_index=True,
    )


def feature_b(raw_reviews, reviews):
    st.subheader("Feature B: Review sentiment")
    st.write("Inspect review volume and the prepared sentiment labels from the Feature B artifact.")
    category = st.selectbox(
        "Review category",
        ["All categories"] + sorted(reviews["category"].unique()),
        key="feature_b_category",
    )
    sentiment = st.multiselect(
        "Sentiment",
        sorted(reviews["sentiment"].unique()),
        default=sorted(reviews["sentiment"].unique()),
        key="feature_b_sentiment",
    )
    filtered = reviews.copy()
    if category != "All categories":
        filtered = filtered[filtered["category"] == category]
    if sentiment:
        filtered = filtered[filtered["sentiment"].isin(sentiment)]
    metric_col, chart_col = st.columns([1, 2])
    with metric_col:
        st.metric("Source products", f"{raw_reviews.shape[0]:,}")
        st.metric("Reviews in view", f"{filtered.shape[0]:,}")
    with chart_col:
        counts = filtered["sentiment"].value_counts().rename_axis("sentiment").to_frame("reviews")
        st.bar_chart(counts, color="#d97757")
    st.dataframe(
        filtered[["productName", "sentiment", "review"]].head(100),
        use_container_width=True,
        hide_index=True,
    )


def feature_c(images):
    st.subheader("Feature C: Image library")
    st.write("Browse the downloaded product images by search keyword and inspect the image inventory.")
    if images.empty:
        st.warning(f"No images found in {IMAGE_DIR}.")
        return
    keyword = st.selectbox(
        "Search keyword",
        ["All keywords"] + sorted(images["keyword"].unique()),
        key="feature_c_keyword",
    )
    limit = st.slider("Images to display", 4, 24, 12, key="feature_c_limit")
    filtered = images if keyword == "All keywords" else images[images["keyword"] == keyword]
    st.metric("Images available", f"{len(filtered):,}")
    columns = st.columns(4)
    for index, item in enumerate(filtered.head(limit).itertuples(index=False)):
        with columns[index % 4]:
            st.image(Image.open(item.path), caption=item.filename, use_container_width=True)


def feature_d(frame):
    st.subheader("Feature D: Price intelligence")
    st.write("Compare price distributions and price tiers across product categories.")
    category = st.selectbox(
        "Price category",
        ["All categories"] + sorted(frame["category"].unique()),
        key="feature_d_category",
    )
    filtered = frame if category == "All categories" else frame[frame["category"] == category]
    metric_cols = st.columns(4)
    metric_cols[0].metric("Products", f"{len(filtered):,}")
    metric_cols[1].metric("Median price", f"${filtered['price_value'].median():,.2f}")
    metric_cols[2].metric("Average rating", f"{filtered['rating'].mean():.2f}")
    metric_cols[3].metric("Brands", f"{filtered['brand'].nunique():,}")

    chart_col, tier_col = st.columns(2)
    with chart_col:
        st.caption("Price distribution")
        st.bar_chart(filtered["price_value"].round(0).value_counts().sort_index(), color="#287c7c")
    with tier_col:
        st.caption("Price tier mix")
        st.bar_chart(filtered["price_tier"].value_counts().sort_index(), color="#d97757")
    table = filtered[["category", "title", "brand", "price_value", "rating", "rating_count", "price_tier"]].copy()
    table["price_value"] = table["price_value"].map(lambda value: f"${value:,.2f}")
    st.dataframe(table.sort_values("rating", ascending=False).head(100), use_container_width=True, hide_index=True)


def main():
    show_header()
    similarity = load_similarity_data()
    price = load_price_data()
    raw_reviews, reviews = load_reviews()
    images = load_images()
    tabs = st.tabs(["Feature A | Similarity", "Feature B | Reviews", "Feature C | Images", "Feature D | Pricing"])
    with tabs[0]:
        feature_a(similarity)
    with tabs[1]:
        feature_b(raw_reviews, reviews)
    with tabs[2]:
        feature_c(images)
    with tabs[3]:
        feature_d(price)


if __name__ == "__main__":
    main()
