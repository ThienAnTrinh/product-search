from pathlib import Path
import yaml

import sys
sys.path.insert(1, "app")
from utils.prepare_data import get_data, prepare_documents
from utils.vectordb import Vectorstore


with open("app/utils/config.yml", "r") as file:
    config = yaml.safe_load(file)


def test_app():

    data = get_data()
    data = data[:1]
    docs = prepare_documents(data)

    assert "id" in data
    assert "text" in data
    assert "title" in data
    assert "description" in data
    assert "price" in data

    db = Vectorstore()
    db.add_documents(docs)
    docs = db.search("high quality")

    assert docs[0].page_content
    metadata = docs[0].metadata
    assert "id" in metadata
    assert "title" in metadata
    assert "description" in metadata
    assert "price" in metadata


def test_db_dir():
    assert Path("app", config["db_path"]).exists()
