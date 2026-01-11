import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os
from typing import List, Dict, Optional, Any
import logging
from pathlib import Path
import uuid
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ChromaClient:
    """Wrapper for ChromaDB to manage persistent vector storage."""
    
    def __init__(self, persist_directory: str = "chroma_db", collection_name: str = "intelligence_knowledge"):
        """Initialize ChromaDB client with persistence."""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Ensure directory exists
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        try:
            # Initialize client with new standard in 0.4.x+
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # Use default embedding function (all-MiniLM-L6-v2)
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            
            logger.info(f"Initialized ChromaDB in {persist_directory} with collection '{collection_name}'")
            logger.info(f"Current collection count: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of dicts, each must have 'content' and optional metadata.
            
        Returns:
            Number of documents added.
        """
        if not documents:
            return 0
            
        ids = []
        texts = []
        metadatas = []
        
        for doc in documents:
            # Generate ID if not provided
            doc_id = doc.get("id", str(uuid.uuid4()))
            content = doc.get("content")
            
            if not content:
                logger.warning(f"Skipping document {doc_id} with no content")
                continue
                
            ids.append(doc_id)
            texts.append(content)
            
            # Prepare metadata
            meta = doc.get("metadata", {}).copy()
            # Ensure timestamp
            if "timestamp" not in meta:
                meta["timestamp"] = datetime.utcnow().isoformat()
            # Store source if available
            if "source" in doc:
                meta["source"] = doc["source"]
                
            metadatas.append(meta)
            
        try:
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(ids)} documents to ChromaDB")
            return len(ids)
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            return 0

    def query_similar(self, query_text: str, n_results: int = 5, where: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query_text: The search query.
            n_results: Number of results to return.
            where: Optional metadata filters.
            
        Returns:
            List of result dictionaries.
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            
            formatted_results = []
            
            # Parse the column-based results from Chroma
            if results["ids"] and len(results["ids"]) > 0:
                for i in range(len(results["ids"][0])):
                    item = {
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None
                    }
                    formatted_results.append(item)
                    
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []

    def count(self) -> int:
        """Return total number of documents in collection."""
        return self.collection.count()

    def reset(self):
        """Clear all data from the collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn
            )
            logger.info("Reset ChromaDB collection")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
