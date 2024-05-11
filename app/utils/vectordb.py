import yaml
import torch
import shutil
from pathlib import Path

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from typing import List



with open("app/utils/config.yml", "r") as file:
    config = yaml.safe_load(file)


class Vectorstore():

    def __init__(self) -> None:

        path = Path("app", config["db_path"])
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)

        if torch.cuda.is_available():
            model_kwargs = {"device": config.get("device", "cpu")}
        else:
            model_kwargs = {"device": "cpu"}
        encode_kwargs = {"normalize_embeddings": config["normalize_embeddings"]}
        
        embeddings = HuggingFaceBgeEmbeddings(
            model_name=config["embedding_model"],
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        
        self.db = Chroma(
            embedding_function=embeddings,
            persist_directory=str(path)
        )


    def add_documents(self, docs: List[Document]) -> None:
        return self.db.add_documents(docs)
    

    def search(self, query) -> tuple[List[dict]]:
        return self.db.similarity_search(query, k=10)
    

    def load(self):
        return self
    