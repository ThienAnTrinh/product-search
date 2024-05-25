import yaml
from utils.vectordb import Vectorstore
from utils.pydanticInputs import Input

from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
import uvicorn

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")


with open("utils/config.yml", "r") as file:
    config = yaml.safe_load(file)
db = Vectorstore(config)


# ============

app = FastAPI()


@app.post("/create-embeddings")
async def embed(db: Vectorstore = Depends(db())):
    try:
        db.add_data()
    except Exception as error_message:
        raise HTTPException(status_code=500, detail=error_message)


@app.post("/search")
async def search(
    input: Input,
    db: Annotated[dict, Depends(db())]
):
    try:
        response = db.search(input.query)
        return {"result": response}
    except KeyError as e:
        error_message = f"KeyError occurred: {e}"
        raise HTTPException(status_code=500, detail=error_message)

    except ValueError as e:
        error_message = f"ValueError occurred: {e}"
        raise HTTPException(status_code=500, detail=error_message)

    except Exception as e:
        error_message = f"An unexpected Exception occurred: {e}"
        raise HTTPException(status_code=500, detail=error_message)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
