import requests
import uuid
from utils.database import get_supabase_admin
from utils.chroma_client import chroma_client
from utils.mistral_client import ai_client
from utils.config import PARSING_SERVICE_URL
from models.schemas import DocumentUpload
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.supabase = get_supabase_admin()
    
    async def upload_and_process_document(self, file, title: str, user_id: str) -> dict:
        """Upload and process a document"""
        try:
            # Send file to parsing service
            files = {'file': (file.filename, file.file, file.content_type)}
            response = requests.post(f"{PARSING_SERVICE_URL}/parse-pdf", files=files)
            
            if response.status_code != 200:
                raise Exception(f"Parsing service error: {response.json().get('error', 'Unknown error')}")
            
            parsed_data = response.json()
            chunks = parsed_data['chunks']
            
            # Generate embeddings for chunks
            embeddings = await ai_client.generate_embeddings(chunks)
            
            # Extract topics using LLM
            topics = await self._extract_topics(parsed_data['text'])
            
            # Generate unique IDs for chunks
            chunk_ids = [f"{user_id}_{uuid.uuid4()}" for _ in chunks]
            
            # Prepare metadata for ChromaDB
            # Convert topics list to comma-separated string for ChromaDB
            topics_str = ", ".join(topics) if topics else ""
            metadatas = [
                {
                    "user_id": str(user_id),
                    "document_title": str(title),
                    "chunk_index": str(i),
                    "topics": topics_str
                }
                for i in range(len(chunks))
            ]
            
            # Store embeddings in ChromaDB
            chroma_client.add_documents(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            # Store document metadata in Supabase
            document_id = str(uuid.uuid4())
            document_record = {
                "id": document_id,
                "user_id": user_id,
                "title": title,
                "filename": file.filename,
                "topics": topics,
                "chunk_count": len(chunks)
            }
            
            result = self.supabase.table("documents").insert(document_record).execute()
            
            # Store topics in topics table
            for topic in topics:
                topic_record = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "document_id": document_id,
                    "name": topic
                }
                self.supabase.table("topics").insert(topic_record).execute()
            
            logger.info(f"Document processed successfully: {title}")
            
            return {
                "document_id": document_id,
                "title": title,
                "topics": topics,
                "chunk_count": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise
    
    async def _extract_topics(self, text: str) -> list:
        """Extract topics from document text using LLM"""
        try:
            prompt = f"""Analyze the following text and extract 3-5 main topics or subjects covered. 
            Return only a JSON array of topic names as strings, no additional text.
            
            Text:
            {text[:2000]}...
            """
            
            messages = [{"role": "user", "content": prompt}]
            response = await ai_client.chat_completion(messages, max_tokens=200)
            
            # Parse JSON response
            import json
            topics = json.loads(response.strip())
            
            # Ensure topics is a list and contains only strings
            if isinstance(topics, list):
                # Filter out non-string items and limit to 5 topics
                string_topics = [str(topic) for topic in topics if topic][:5]
                return string_topics if string_topics else ["General Study Material"]
            else:
                logger.warning(f"LLM returned non-list response: {topics}")
                return ["General Study Material"]
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            # Fallback to generic topic
            return ["General Study Material"]
    
    async def get_user_documents(self, user_id: str) -> list:
        """Get all documents for a user"""
        try:
            result = self.supabase.table("documents").select("*").eq("user_id", user_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting user documents: {e}")
            raise
    
    async def get_user_topics(self, user_id: str) -> list:
        """Get all topics for a user"""
        try:
            result = self.supabase.table("topics").select("name").eq("user_id", user_id).execute()
            topics = list(set([item["name"] for item in result.data]))
            return topics
        except Exception as e:
            logger.error(f"Error getting user topics: {e}")
            raise
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document and its associated data"""
        try:
            logger.info(f"Starting deletion of document {document_id} for user {user_id}")
            
            # First get the document title to match ChromaDB metadata
            doc_result = self.supabase.table("documents").select("title").eq("id", document_id).eq("user_id", user_id).execute()
            
            if not doc_result.data:
                logger.warning(f"Document {document_id} not found for user {user_id}")
                raise Exception(f"Document not found or you don't have permission to delete it")
            
            document_title = doc_result.data[0]["title"]
            logger.info(f"Found document to delete: '{document_title}'")
            
            # Delete from ChromaDB using document_title (as stored in metadata)
            try:
                chroma_client.delete_user_documents(user_id, document_title)
                logger.info(f"Successfully deleted document chunks from ChromaDB")
            except Exception as chroma_error:
                logger.error(f"Error deleting from ChromaDB: {chroma_error}")
                raise Exception(f"Failed to delete document from vector database: {str(chroma_error)}")
            
            # Delete from Supabase tables
            try:
                # Delete topics first (foreign key constraint)
                topics_result = self.supabase.table("topics").delete().eq("document_id", document_id).eq("user_id", user_id).execute()
                logger.info(f"Deleted {len(topics_result.data) if topics_result.data else 0} topic records")
                
                # Delete document record
                doc_delete_result = self.supabase.table("documents").delete().eq("id", document_id).eq("user_id", user_id).execute()
                logger.info(f"Deleted {len(doc_delete_result.data) if doc_delete_result.data else 0} document records")
                
            except Exception as supabase_error:
                logger.error(f"Error deleting from Supabase: {supabase_error}")
                raise Exception(f"Failed to delete document from database: {str(supabase_error)}")
            
            logger.info(f"Successfully completed deletion of document: {document_title} (ID: {document_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise

document_service = DocumentService()
