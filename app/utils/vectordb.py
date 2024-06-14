from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from loguru import logger
from opentelemetry import trace
from opentelemetry.trace import get_tracer_provider
from utils.prepare_data import get_data, prepare_documents

tracer = get_tracer_provider().get_tracer("app", "0.0.1")

# ============


class Vectorstore:
    def __init__(self, config) -> None:

        self.db = PineconeVectorStore(
            index_name=config["vector_store_config"]["pinecone_index_name"],
            embedding=OpenAIEmbeddings(
                model=config["vector_store_config"]["embedding_model"],
                dimensions=config["vector_store_config"]["embedding_dim"],
            ),
        )

    def add_data(self) -> None:

        with tracer.start_as_current_span("processors") as processors:

            # Remove old data
            try:
                with tracer.start_as_current_span(
                    "remove-old-data",
                    links=[trace.Link(processors.get_span_context())],
                ):
                    self.db.delete(delete_all=True)
                logger.info("Emptied database.")
            except Exception as e:
                logger.error(f"Failed to empty database: {e}")

            # Retrieve and preprocess data
            try:
                with tracer.start_as_current_span(
                    "retrieve-preprocess",
                    links=[trace.Link(processors.get_span_context())],
                ):
                    data = get_data()
                logger.info("Finished retrieving and preprocessing data.")
            except Exception as e:
                logger.error(f"Failed to get data: {e}")

            # Prepare data for DB
            try:
                with tracer.start_as_current_span(
                    "prepare-data",
                    links=[trace.Link(processors.get_span_context())],
                ):
                    docs = prepare_documents(data)
                    texts, metadatas = zip(
                        *[(doc.page_content, doc.metadata) for doc in docs],
                    )
                logger.info("Finished preparing data for DB.")
            except Exception as e:
                logger.error(f"Failed to prepare data for BD: {e}")

            # Embed data
            try:
                with tracer.start_as_current_span(
                    "add-texts-to-db",
                    links=[trace.Link(processors.get_span_context())],
                ):
                    self.db.add_texts(
                        texts=texts,
                        metadatas=metadatas,
                        embedding_chunk_size=500,
                        batch_size=128,
                    )
                logger.info("Finished embedding data to database.")
            except Exception as e:
                logger.error(f"Failed to embed data to database: {e}")

    def search(self, query) -> tuple[list[dict]]:

        with tracer.start_as_current_span("processors") as processors:
            with tracer.start_as_current_span(
                "search",
                links=[trace.Link(processors.get_span_context())],
            ):
                results = self.db.similarity_search(query, k=5)
                response = [
                    {
                        "id": result.metadata["id"],
                        "title": result.metadata["title"],
                        "brand": result.metadata["brand"],
                        "price": result.metadata["price"],
                        "description": result.metadata["description"],
                    }
                    for result in results
                ]

        logger.info(
            {
                "Query": query,
                "Result": response,
            },
        )
        return response

    def __call__(self):
        return self
