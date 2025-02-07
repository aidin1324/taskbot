from uuid import uuid4
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import core.config as config

data_dir = "data"


class VectorDB:
    def __init__(
        self,
        api_key: str,
        model: str,
        collection_name: str
    ):
        self._api_key = api_key
        self._embedding = OpenAIEmbeddings(model=model, api_key=api_key)
        self.collection_name = collection_name
        self._vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self._embedding,
            persist_directory=data_dir,
            collection_metadata={"hnsw:space": "cosine"}
        )
        
    def from_documents(self, documents: list[Document]):
        try:
            uids = [str(uuid4()) for _ in range(len(documents))]
            self._vector_store.add_documents(documents=documents, ids=uids)
        except Exception as e:
            raise ValueError(f"Error adding documents to vector store: {e}")
       
    def add_item(self, document: Document):
        try:
            uid = str(uuid4())
            self._vector_store.add_document(document=document, id=uid)
            return uid
        except Exception as e:
            raise ValueError(f"Error adding document to vector store: {e}")
        
    def update_items(self, documents: list[Document], uuids: list[str]):
        try:
            self._vector_store.update_documents(documents=documents, ids=uuids)
        except Exception as e:
            raise ValueError(f"Error updating documents in vector store: {e}")
        
    def query(self, query: str, top_k: int):
        try:
            responses = self._vector_store.similarity_search(k=top_k, query=query)
            return responses
        except Exception as e:
            raise ValueError(f"Error querying vector store: {e}")
    
    def delete_items(self, uuids: list[str]):
        try:
            self._vector_store.delete(ids=uuids)
        except Exception as e:
            raise ValueError(f"Error deleting documents from vector store: {e}")