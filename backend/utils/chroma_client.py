import chromadb
from chromadb.config import Settings
from utils.config import CHROMA_DB_PATH
import logging

logger = logging.getLogger(__name__)

class ChromaDBClient:
    def __init__(self):
        # Ensure ChromaDB directory exists with proper permissions
        import os
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        os.chmod(CHROMA_DB_PATH, 0o755)
        
        self.client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection_name = "kashar_documents"
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or get existing collection"""
        try:
            # Try to get existing collection first
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"ChromaDB collection '{self.collection_name}' found")
            except Exception:
                # Collection doesn't exist, create new one
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Kashar AI document embeddings with OpenAI embeddings"}
                )
                logger.info(f"ChromaDB collection '{self.collection_name}' created")
                
        except Exception as e:
            # If there's a dimension mismatch, delete and recreate collection
            logger.warning(f"Collection issue detected: {e}")
            try:
                self.client.delete_collection(name=self.collection_name)
                logger.info(f"Deleted existing collection '{self.collection_name}' due to dimension mismatch")
            except:
                pass
            
            # Create new collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Kashar AI document embeddings with OpenAI embeddings"}
            )
            logger.info(f"ChromaDB collection '{self.collection_name}' recreated with correct dimensions")
    
    def add_documents(self, documents: list, embeddings: list, metadatas: list, ids: list):
        """Add documents to the collection"""
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to ChromaDB")
        except Exception as e:
            # Check if it's a dimension mismatch error
            if "dimension" in str(e).lower():
                logger.warning(f"Dimension mismatch detected: {e}")
                # Recreate collection and try again
                try:
                    self.client.delete_collection(name=self.collection_name)
                    self.collection = self.client.create_collection(
                        name=self.collection_name,
                        metadata={"description": "Kashar AI document embeddings with OpenAI embeddings"}
                    )
                    logger.info(f"Recreated collection '{self.collection_name}' with correct dimensions")
                    
                    # Try adding documents again
                    self.collection.add(
                        documents=documents,
                        embeddings=embeddings,
                        metadatas=metadatas,
                        ids=ids
                    )
                    logger.info(f"Added {len(documents)} documents to ChromaDB after recreation")
                except Exception as retry_error:
                    logger.error(f"Error adding documents after recreation: {retry_error}")
                    raise
            else:
                logger.error(f"Error adding documents to ChromaDB: {e}")
                raise
    
    def query_documents(self, query_embeddings: list, n_results: int = 5, where: dict = None):
        """Query documents from the collection"""
        try:
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where
            )
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            raise
    
    def delete_user_documents(self, user_id: str, document_title: str = None):
        """Delete documents for a specific user, optionally filtered by document title"""
        try:
            if document_title:
                # Delete specific document by title using AND operator
                self.collection.delete(where={"$and": [{"user_id": {"$eq": user_id}}, {"document_title": {"$eq": document_title}}]})
                logger.info(f"Deleted document '{document_title}' for user {user_id}")
            else:
                # Delete all documents for user
                self.collection.delete(where={"user_id": user_id})
                logger.info(f"Deleted all documents for user {user_id}")
        except Exception as e:
            logger.error(f"Error deleting user documents: {e}")
            raise

# Global ChromaDB client instance
chroma_client = ChromaDBClient()
