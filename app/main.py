from utils.prepare_data import get_data, prepare_documents
from utils.vectordb import Vectorstore
from utils.pydanticInputs import Input
from utils.config import load_config

from typing import Annotated
from fastapi import FastAPI, Depends
# import uvicorn


db = Vectorstore(load_config())

data = get_data()
docs = prepare_documents(data)

db.add_documents(docs)


# ============

app = FastAPI()


@app.post("/search")
async def search(
    input: Input,
    db: Annotated[dict, Depends(db.load)]
):
    retrieved_docs = db.search(input.query)
    response = [retrieved_doc.metadata for retrieved_doc in retrieved_docs]
    return {"result": response}


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8001)
