import re

from datasets import disable_caching, load_dataset
from langchain_core.documents import Document
from loguru import logger
from opentelemetry.trace import get_tracer_provider

tracer = get_tracer_provider().get_tracer("app", "0.0.1")

# ============


def clean_text(text):
    output_string = re.sub(
        r"\"@en-US|\\\"|@en|</?li>|</?ul>|<br\s?/?>",
        "",
        text,
    ).replace('"', "")
    output_string = re.sub(r"[\n\t]+", " ", output_string)
    output_string = re.sub(r"\s+", " ", output_string).strip()
    return output_string


def concat_title_description(example):
    example["id"] = example["id_left"]
    example["title"] = (
        clean_text(example["title_left"]) if example["title_left"] else ""
    )
    example["description"] = (
        clean_text(example["description_left"]) if example["description_left"] else ""
    )
    example["text"] = example["description"] + " " + example["title"]
    example["brand"] = (
        clean_text(example["brand_left"]) if example["brand_left"] else ""
    )
    example["price"] = (
        clean_text(example["price_left"]) if example["price_left"] else ""
    )
    return example


def get_data():
    disable_caching()
    dataset = load_dataset(
        "wdc/products-2017",
        "cameras_medium",
        split="validation",
        download_mode="force_redownload",
    )
    updated_dataset = dataset.map(concat_title_description, load_from_cache_file=False)
    return updated_dataset


def prepare_documents(dataset):

    docs = []
    for id, title, description, text, brand, price in zip(
        dataset["id"],
        dataset["title"],
        dataset["description"],
        dataset["text"],
        dataset["brand"],
        dataset["price"],
    ):
        doc = Document(
            page_content=text,
            metadata={
                "id": id,
                "title": title,
                "description": description[:500],
                "brand": brand,
                "price": price,
            },
        )
        docs.append(doc)

    return docs
