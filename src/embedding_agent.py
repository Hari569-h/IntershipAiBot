"""
AI Embedding Agent for generating text embeddings with Cohere v3 and fallback to OpenAI.
"""
import os
import time
import logging
from typing import List, Optional, Dict, Any
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import backoff
import numpy as np
import cohere
from openai import OpenAI

# Disable tokenizers parallelism to avoid deadlocks in forks
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger(__name__)

class EmbeddingAgent:
    """
    AI Embedding Agent that generates embeddings using Cohere v3 with fallback to OpenAI.
    Implements timeout, retry logic, and dimension validation.
    """
    
    COHERE_EMBED_DIM = 1024  # Cohere v3 embedding dimension
    EMBEDDING_TIMEOUT = 30  # seconds
    MAX_RETRIES = 2
    
    def __init__(self, cohere_api_key: str, openai_api_key: Optional[str] = None):
        """
        Initialize the Embedding Agent.
        
        Args:
            cohere_api_key: API key for Cohere
            openai_api_key: Optional API key for OpenAI fallback
        """
        self.cohere_client = cohere.Client(cohere_api_key)
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        self._validate_cohere_connection()
    
    def _validate_cohere_connection(self):
        """Validate Cohere connection and model availability."""
        try:
            # Simple validation by getting a small embedding
            test_embedding = self._get_cohere_embedding(["test"])[0]
            if len(test_embedding) != self.COHERE_EMBED_DIM:
                raise ValueError(
                    f"Unexpected embedding dimension: {len(test_embedding)}. "
                    f"Expected: {self.COHERE_EMBED_DIM}"
                )
        except Exception as e:
            logger.error(f"Failed to validate Cohere connection: {str(e)}")
            raise
    
    @backoff.on_exception(
        backoff.expo,
        (Exception,),
        max_tries=MAX_RETRIES + 1,
        giveup=lambda e: isinstance(e, (ValueError, cohere.CohereError)),
        logger=logger
    )
    def _get_cohere_embedding(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings from Cohere with retry logic and timeout.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                self.cohere_client.embed,
                model="embed-english-v3.0",
                texts=texts,
                input_type="search_document"
            )
            
            try:
                response = future.result(timeout=self.EMBEDDING_TIMEOUT)
                embeddings = response.embeddings
                
                # Validate embedding dimensions
                if any(len(emb) != self.COHERE_EMBED_DIM for emb in embeddings):
                    raise ValueError("Invalid embedding dimension received from Cohere")
                    
                return embeddings
                
            except FutureTimeoutError:
                logger.warning("Cohere embedding request timed out")
                raise TimeoutError("Cohere embedding request timed out")
            except Exception as e:
                logger.error(f"Error getting Cohere embeddings: {str(e)}")
                raise
    
    def _get_openai_embedding(self, texts: List[str]) -> List[List[float]]:
        """
        Fallback method to get embeddings from OpenAI.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not configured")
            
        try:
            response = self.openai_client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Error getting OpenAI embeddings: {str(e)}")
            raise
    
    def get_embeddings(
        self, 
        texts: List[str], 
        batch_size: int = 32
    ) -> List[List[float]]:
        """
        Get embeddings for a list of texts with Cohere as primary and OpenAI as fallback.
        
        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
            
        # Process in batches
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # Try Cohere first
                embeddings = self._get_cohere_embedding(batch)
            except Exception as e:
                logger.warning(f"Falling back to OpenAI due to: {str(e)}")
                try:
                    embeddings = self._get_openai_embedding(batch)
                except Exception as fallback_error:
                    logger.error(f"Both Cohere and OpenAI failed: {str(fallback_error)}")
                    # Return partial results if we have any, otherwise raise
                    if all_embeddings:
                        logger.warning("Returning partial results after failure")
                        return all_embeddings + [[]] * (len(texts) - len(all_embeddings))
                    raise
            
            all_embeddings.extend(embeddings)
        
        return all_embeddings
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        return self.get_embeddings([text])[0]
    
    def batch_get_embeddings(
        self, 
        texts_list: List[List[str]], 
        max_workers: int = 4
    ) -> List[List[List[float]]]:
        """
        Process multiple batches of texts in parallel.
        
        Args:
            texts_list: List of text batches to process
            max_workers: Maximum number of parallel workers
            
        Returns:
            List of embedding batches
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.get_embeddings, batch)
                for batch in texts_list
            ]
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.error(f"Error in batch processing: {str(e)}")
                    results.append([])
                    
        return results
