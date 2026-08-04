import logging
from fastapi import FastAPI
from inngest import Inngest,PydanticSerializer,TriggerEvent,Context
from inngest.fast_api import serve
from inngest.experimental import ai
from dotenv import load_dotenv
import uuid
import os
import datetime
from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from custom_types import RAGChunkAndSrc, RAGSearchResult, RAGUpsertResult

load_dotenv()  # Load environment variables from .env file

inngest_client = Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicron"),
    is_production=False,
    serializer=PydanticSerializer(),
)

@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=TriggerEvent(event="rag/ingest_pdf"),
    
)
async def rag_ingest_pdf(ctx: Context) -> str:
    def _load(ctx: Context) -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunk=chunks, source_id=source_id)
        
    
    def _upsert(chunk_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        chunks = chunk_and_src.chunk
        source_id = chunk_and_src.source_id
        vecs = embed_texts(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL,f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]
        QdrantStorage().upsert(ids, vecs, payloads)
        return RAGUpsertResult(ingested=len(chunks))
    
    #return f"PDF Ingested at {datetime.datetime.now()} with context: {ctx.event.data}"
    chunks_and_src = await ctx.step.run("load-and-chunk",
                                        lambda: _load(ctx),
                                        output_type=RAGChunkAndSrc)
    ingested = await ctx.step.run("embed-and-upsert",
                                  lambda: _upsert(chunks_and_src),
                                  output_type=RAGUpsertResult)
    
    return ingested.model.dump()

app = FastAPI()
serve(app, inngest_client,[rag_ingest_pdf])

