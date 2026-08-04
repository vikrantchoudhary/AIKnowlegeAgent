from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance    
class QdrantStorage:
    def __init__(self, url="http://localhost:6333", collection="docs",dim=384):
        self.client = QdrantClient(url=url,timeout=30)
        self.collection = collection
        
        if self.client.collection_exists(self.collection):
            info = self.client.get_collection(self.collection)
            current_dim = info.config.params.vectors.size
            if current_dim != dim:
                print(f"Collection '{self.collection}' exists with dimension {current_dim}, but expected dimension is {dim}.")
                self.client.delete_collection(self.collection)
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )
        #if not self.client.has_collection(self.collection):
        #    self.client.create_collection(
        #        collection_name=self.collection,
        #        vectors_config=VectorParams(size=din, distance=Distance.COSINE),
        #    )
    def upsert(self, ids, vectors, payloads):
        #points = [PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
        points = [
            PointStruct(id=idx, vector=vec, payload=pay) 
            for idx, vec, pay in zip(ids, vectors, payloads)
        ]
        self.client.upsert(self.collection, points=points)
    
    def search(self, query_vector, top_k: int=5):
        #search_result = self.client.search(
        #    collection_name=self.collection,
        #    query_vector=query_vector,
        #    with_payload=True,
        #    limit=top_k
        #)
        search_result = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            with_payload=True,
            limit=top_k
        )
        #return search_result
        contexts = []
        sources = []
        for r in search_result.points:
            #payload = getattr(r, 'payload', None) or {}
            payload = r.payload or {}
            text = payload.get('text', '')
            source = payload.get('source', '')
            if text:
                contexts.append(text)
                sources.append(source)
    
        return {"contexts": contexts, "sources" :list(sources)}