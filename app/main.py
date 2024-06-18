import os
from typing import Annotated

import uvicorn
import yaml
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from utils.pydanticInputs import Input
from utils.vectordb import Vectorstore


# Load environment variables

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")


# Jaeger for tracing

trace_provider = TracerProvider(
    resource=Resource.create({SERVICE_NAME: "product-search-service"}),
)

jaeger_exporter = JaegerExporter(
    agent_host_name=os.getenv("JAEGER_AGENT_HOST"),
    agent_port=int(os.getenv("JAEGER_AGENT_PORT")),
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace_provider.add_span_processor(span_processor)
trace.set_tracer_provider(trace_provider)


# ============

# load config and vectore store
with open("utils/config.yml") as file:
    config = yaml.safe_load(file)
db = Vectorstore(config)


# ============

app = FastAPI()

# Instrument FastAPI app
FastAPIInstrumentor.instrument_app(app, tracer_provider=trace_provider)


# endpoint to create embedding in vectorstore
@app.post("/create-embeddings")
async def embed(db: Vectorstore = Depends(db())):
    try:
        db.add_data()
    except Exception as error_message:
        raise HTTPException(status_code=500, detail=error_message)

# endpoint for product search
@app.post("/search")
async def search(
    input: Input,
    db: Annotated[dict, Depends(db())],
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
