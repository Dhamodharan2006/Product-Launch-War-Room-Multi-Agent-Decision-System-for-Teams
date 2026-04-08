"""LlamaIndex RAG setup for user feedback analysis."""

import os
from typing import List, Dict, Any
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter


class FeedbackRAG:
    """
    RAG system for querying user feedback.
    
    NOTE: This uses a LOCAL embedding model (BAAI/bge-small-en-v1.5) for vector 
    similarity search, NOT the Groq LLM. Groq API is only for text generation 
    (LLM), while embeddings are computed locally for efficiency and cost savings.
    """
    
    def __init__(self):
        # Use lightweight local embedding model (runs on CPU, ~133MB download)
        # This is separate from Groq API which handles LLM inference
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        self.index = None
        self.documents = []
    
    def load_feedback(self, feedback_data: List[Dict[str, Any]]):
        """Load feedback into vector store."""
        self.documents = []
        
        for item in feedback_data:
            # Create rich text representation
            text = f"""
            User Feedback [{item.get('id')}]:
            Segment: {item.get('user_segment', 'unknown')}
            Category: {item.get('category', 'unknown')}
            Sentiment Score: {item.get('sentiment_score', 0.5)}
            Source: {item.get('source', 'unknown')}
            Timestamp: {item.get('timestamp', '')}
            
            Content: {item.get('text', '')}
            """
            
            doc = Document(
                text=text,
                metadata={
                    "id": item.get("id"),
                    "category": item.get("category"),
                    "sentiment_score": item.get("sentiment_score"),
                    "segment": item.get("user_segment"),
                    "source": item.get("source")
                }
            )
            self.documents.append(doc)
        
        # Build index
        parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
        nodes = parser.get_nodes_from_documents(self.documents)
        self.index = VectorStoreIndex(nodes)
    
    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query feedback for specific patterns."""
        if not self.index:
            return []
        
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query_text)
        
        results = []
        for node in nodes:
            results.append({
                "text": node.node.text,
                "score": node.score,
                "metadata": node.node.metadata
            })
        
        return results
    
    def get_similar_issues(self, issue_type: str, count: int = 5) -> List[Dict[str, Any]]:
        """Find feedback similar to a specific issue type."""
        queries = {
            "crash": "app crash freeze hang error bug",
            "payment": "payment failed checkout billing charge",
            "ui": "confusing interface button layout design",
            "performance": "slow loading lag speed performance"
        }
        
        query = queries.get(issue_type, issue_type)
        return self.query(query, top_k=count)


# Global instance
feedback_rag = FeedbackRAG()