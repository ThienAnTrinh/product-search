import sys
sys.path.insert(1, "app")
import yaml

from utils.vectordb import Vectorstore

# =============

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")

# =============


with open("app/utils/config.yml", "r") as file:
    config = yaml.safe_load(file)


def test_app():

    db = Vectorstore(config=config)

    docs = db.search("high quality")
    assert type(docs) == list

    if not docs:
        db.add_data()
    
    docs = db.search("high quality")
    assert type(docs) == list

    assert type(docs[0]) == dict
    assert "id" in docs[0]
    assert "title" in docs[0]
    assert "description" in docs[0]
    assert "price" in docs[0]
    assert "brand" in docs[0]
