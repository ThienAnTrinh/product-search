from pathlib import Path

import sys
sys.path.insert(1, "app")

from utils.config import load_config_test
from utils.prepare_data import get_data, prepare_documents
from utils.vectordb import Vectorstore


config = load_config_test()


def test_app():

    data = get_data()
    data = data[:1]
    docs = prepare_documents(data)

    assert "id" in data
    assert "text" in data
    assert "title" in data
    assert "description" in data
    assert "price" in data

    db = Vectorstore(config=config)
    assert Path(config["db_path"]).exists()

    db.add_documents(docs)
    docs = db.search("high quality")

    assert docs[0].page_content
    metadata = docs[0].metadata
    assert "id" in metadata
    assert "title" in metadata
    assert "description" in metadata
    assert "price" in metadata
