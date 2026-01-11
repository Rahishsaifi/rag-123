"""
RAG (Retrieval-Augmented Generation) service for orchestrating Q&A over documents.
"""
from typing import List, Dict, Any
from openai import AzureOpenAI
from app.core.config import settings
from app.core.logging import get_logger
from app.services.embedding_service import EmbeddingService
from app.services.search_service import SearchService
from app.models.chat import SourceDocument

logger = get_logger(__name__)


class RAGService:
    """Service for RAG orchestration."""
    
    def __init__(self):
        """Initialize RAG service with dependencies."""
        self.embedding_service = EmbeddingService()
        self.search_service = SearchService()
        self.openai_client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.chat_deployment = settings.azure_openai_chat_deployment
        self.default_top_k = settings.top_k_results
    
    def query(
        self,
        question: str,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Process a question through the RAG pipeline.
        
        Args:
            question: User question
            top_k: Number of documents to retrieve (overrides default)
            
        Returns:
            Dictionary with answer and source documents
        """
        top_k = top_k or self.default_top_k
        
        logger.info(
            f"Processing RAG query",
            extra={
                "extra_fields": {
                    "top_k": top_k,
                    "question_length": len(question)
                }
            }
        )
        
        query_embedding = self.embedding_service.generate_embedding(question)
        search_results = self.search_service.search(
            query_vector=query_embedding,
            top_k=top_k
        )
        
        if not search_results:
            logger.warning("No search results found for query - no documents indexed")
            return {
                "answer": "I cannot answer this question because there are no documents uploaded and indexed yet. Please upload documents first, then ask your question.",
                "sources": [],
                "question": question
            }
        
        context = self._build_context(search_results)
        answer = self._generate_answer(question, context)
        sources = self._format_sources(search_results)
        
        logger.info(
            f"RAG query completed",
            extra={
                "extra_fields": {
                    "answer_length": len(answer),
                    "num_sources": len(sources)
                }
            }
        )
        
        return {
            "answer": answer,
            "sources": sources,
            "question": question
        }
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Build context string from search results.
        
        Args:
            search_results: List of search result dictionaries
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, result in enumerate(search_results, start=1):
            content = result.get("content", "")
            filename = result.get("filename", "unknown")
            chunk_index = result.get("chunk_index", 0)
            
            context_parts.append(
                f"[Document {i}: {filename}, Chunk {chunk_index}]\n{content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using Azure OpenAI chat completion.
        
        Args:
            question: User question
            context: Retrieved context from documents
            
        Returns:
            Generated answer
        """
        system_prompt = """You are a document-based Q&A assistant. Your ONLY source of information is the context provided from uploaded documents.

CRITICAL RULES - YOU MUST FOLLOW THESE STRICTLY:
1. ONLY use information from the provided context to answer questions
2. DO NOT use any knowledge, facts, or information from outside the provided context
3. DO NOT make assumptions or inferences beyond what is explicitly stated in the context
4. If the context doesn't contain enough information to answer the question, you MUST say: "I cannot answer this question based on the provided documents. The information is not available in the uploaded documents."
5. If asked about something not in the documents, explicitly state that it's not in the provided documents
6. When referencing information, mention which document (filename) it came from
7. Be accurate and only state facts that are directly supported by the context
8. Do not add any information, examples, or explanations that are not in the provided context

Remember: You are answering ONLY from the uploaded documents. You have no other knowledge base."""
        
        user_prompt = f"""Below is the context extracted from uploaded documents. Use ONLY this information to answer the question.

CONTEXT FROM UPLOADED DOCUMENTS:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Answer the question using ONLY the information from the context above
- If the answer is not in the context, explicitly state that the information is not available in the uploaded documents
- Do not use any knowledge outside of what is provided in the context
- Reference the document name when citing information

ANSWER (based only on the provided context):"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.chat_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content.strip()
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise Exception(f"Failed to generate answer: {e}")
    
    def _format_sources(self, search_results: List[Dict[str, Any]]) -> List[SourceDocument]:
        """
        Format search results into SourceDocument models.
        
        Args:
            search_results: List of search result dictionaries
            
        Returns:
            List of SourceDocument objects
        """
        sources = []
        
        for result in search_results:
            source = SourceDocument(
                content=result.get("content", ""),
                file_id=result.get("file_id", ""),
                filename=result.get("filename", "unknown"),
                chunk_index=result.get("chunk_index", 0),
                score=result.get("score")
            )
            sources.append(source)
        
        return sources

