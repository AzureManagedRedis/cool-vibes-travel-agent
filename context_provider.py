"""Redis Context Provider configuration for dynamic learning."""
import os
import uuid
import logging
import numpy as np
from typing import Optional, Any, Dict, List
from datetime import datetime
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.utils.vectorize import BaseVectorizer
from openai import AzureOpenAI
from pydantic import Field, PrivateAttr

logger = logging.getLogger(__name__)


class AzureOpenAIVectorizer(BaseVectorizer):
    """Custom vectorizer for Azure OpenAI embeddings."""
    
    model: str
    dims: int = 1536  # text-embedding-3-small dimensions
    _client: Any = PrivateAttr()
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize Azure OpenAI client after Pydantic initialization."""
        self._client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION", "2024-02-15-preview")
        )
        
    def embed(self, text: str, **kwargs):
        """Generate embedding for a single text."""
        response = self._client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def embed_many(self, texts: list[str], **kwargs):
        """Generate embeddings for multiple texts."""
        response = self._client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]


def create_vectorizer() -> AzureOpenAIVectorizer:
    """
    Create Azure OpenAI text vectorizer for embeddings.
    
    Returns:
        Configured AzureOpenAIVectorizer instance
    """
    embedding_deployment = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-3-small')
    
    vectorizer = AzureOpenAIVectorizer(model=embedding_deployment)
    
    logger.info(f"Created vectorizer with model: {embedding_deployment}")
    return vectorizer


def create_search_index(redis_url: str, vectorizer: AzureOpenAIVectorizer) -> SearchIndex:
    """
    Create RedisVL SearchIndex for storing and retrieving user preferences with vectors.
    
    Args:
        redis_url: Redis connection URL
        vectorizer: Vectorizer for generating embeddings
        
    Returns:
        Configured SearchIndex instance
    """
    schema = {
        "index": {
            "name": "user_preferences_idx_vnext",
            "prefix": "cool-vibes-agent-vnext:UserPref:",
            "storage_type": "hash"
        },
        "fields": [
            {"name": "user_name", "type": "tag"},
            {"name": "preference_text", "type": "text"},
            {"name": "source", "type": "tag"},
            {"name": "timestamp", "type": "text"},
            {
                "name": "embedding",
                "type": "vector",
                "attrs": {
                    "dims": vectorizer.dims,
                    "algorithm": "hnsw",
                    "distance_metric": "cosine"
                }
            }
        ]
    }
    
    # Create index with redis URL
    index = SearchIndex.from_dict(schema)
    index.connect(redis_url)
    
    logger.info(f"Created search index: {schema['index']['name']}")
    return index


async def store_preference(
    index: SearchIndex,
    vectorizer: AzureOpenAIVectorizer,
    user_name: str,
    preference_text: str,
    source: str = "manual"
) -> str:
    """
    Store a user preference with vector embedding.
    
    Args:
        index: SearchIndex instance
        vectorizer: Vectorizer for generating embeddings
        user_name: User identifier
        preference_text: The preference text to store
        source: Source of preference (e.g., "seed", "learned")
        
    Returns:
        Redis key of stored preference
    """
    # Generate embedding
    embedding = vectorizer.embed(preference_text)
    
    # Convert embedding list to numpy array of float32 for RedisVL
    embedding_array = np.array(embedding, dtype=np.float32).tobytes()
    
    # Create unique key
    pref_id = str(uuid.uuid4())[:8]
    redis_key = f"cool-vibes-agent-vnext:UserPref:{user_name}:{pref_id}"
    
    # Create document
    doc = {
        "user_name": user_name,
        "preference_text": preference_text,
        "source": source,
        "timestamp": datetime.utcnow().isoformat(),
        "embedding": embedding_array
    }
    
    # Store in Redis
    index.load([doc], keys=[redis_key])
    
    logger.info(f"Stored preference for {user_name}: {preference_text[:50]}...")
    return redis_key


async def retrieve_preferences(
    index: SearchIndex,
    vectorizer: AzureOpenAIVectorizer,
    user_name: str,
    query_text: Optional[str] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve user preferences, optionally filtered by semantic similarity.
    
    Args:
        index: SearchIndex instance
        vectorizer: Vectorizer for generating query embeddings
        user_name: User identifier
        query_text: Optional query for semantic search
        top_k: Number of results to return
        
    Returns:
        List of preference documents with scores
    """
    if query_text:
        # Semantic search
        query_embedding = vectorizer.embed(query_text)
        query = VectorQuery(
            vector=query_embedding,
            vector_field_name="embedding",
            return_fields=["user_name", "preference_text", "source", "timestamp"],
            filter_expression=f"@user_name:{{{user_name}}}",
            num_results=top_k
        )
        results = index.query(query)
    else:
        # Get all preferences for user
        results = index.search(
            filter_expression=f"@user_name:{{{user_name}}}",
            return_fields=["user_name", "preference_text", "source", "timestamp"],
            num_results=top_k
        )
    
    logger.info(f"Retrieved {len(results)} preferences for {user_name}")
    return results
