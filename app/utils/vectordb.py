from utils.prepare_data import get_data, prepare_documents

from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

# from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain_core.documents import Document

from typing import List


class Vectorstore():

    def __init__(self, config) -> None:

        # path = Path(config["db_path"])
        # if path.exists():
        #     shutil.rmtree(path)
        # path.mkdir(parents=True)

        # if torch.cuda.is_available():
        #     model_kwargs = {"device": config.get("device", "cpu")}
        # else:
        #     model_kwargs = {"device": "cpu"}
        # encode_kwargs = {"normalize_embeddings": config["normalize_embeddings"]}
        
        # embeddings = HuggingFaceBgeEmbeddings(
        #     model_name=config["embedding_model"],
        #     model_kwargs=model_kwargs,
        #     encode_kwargs=encode_kwargs
        # )

        # self.db = Chroma(
        #     embedding_function=embeddings,
        #     persist_directory=str(path)
        # )

        self.db = PineconeVectorStore(
            index_name=config["vector_store_config"]["pinecone_index_name"],
            embedding=OpenAIEmbeddings(
                model=config["vector_store_config"]["embedding_model"], 
                dimensions=config["vector_store_config"]["embedding_dim"]
            )
        )

    
    def add_data(self) -> None:

        try:
            self.db.delete(delete_all=True)
        except:
            pass

        data = get_data()
        docs = prepare_documents(data)

        texts, metadatas = zip(*[(doc.page_content, doc.metadata) for doc in docs])
        self.db.add_texts(
            texts=texts,
            metadatas=metadatas,
            embedding_chunk_size=500,
            batch_size=128
        )

        # df = self.create_dataframe()
        # loader = DataFrameLoader(df, page_content_column="EN")
        # texts, metadatas = zip(*[(doc.page_content, doc.metadata) for doc in loader.load()])

        # self.vector_store.add_texts(
        #     texts=texts,
        #     metadatas=metadatas,
        #     embedding_chunk_size=500,
        #     batch_size=32
        # )


    # def add_documents(self, docs: List[Document]) -> None:
    #     return self.db.add_documents(docs)
    

    def search(self, query) -> tuple[List[dict]]:

        results = self.db.similarity_search(query, k=5)
        response = [{
            "id": result.metadata["id"],
            "title": result.metadata["title"],
            "brand": result.metadata["brand"],
            "price": result.metadata["price"],
            "description": result.metadata["description"]
        }
        for result in results
        ]
        return response
    

    def __call__(self):
        return self
    