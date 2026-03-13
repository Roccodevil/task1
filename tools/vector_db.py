import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec

class VectorDBTool:
    def __init__(self, index_name="agentic-explainer-index"):
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = index_name
        
        # Initialize modern Pinecone client
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Use a lightweight, CPU-friendly embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Creates the Pinecone index if it doesn't exist."""
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=384, # Dimension for all-MiniLM-L6-v2
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )

    def store_document(self, text):
        """Chunks the text and stores it in Pinecone."""
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(text)
        
        # Store using the modern PineconeVectorStore
        PineconeVectorStore.from_texts(
            texts=chunks, 
            embedding=self.embeddings, 
            index_name=self.index_name
        )
        return "Document successfully embedded and stored in Vector DB."

    def query_context(self, query, k=3):
        """Retrieves the most relevant chunks based on the user's doubt."""
        # Query using the modern PineconeVectorStore
        vectorstore = PineconeVectorStore(index_name=self.index_name, embedding=self.embeddings)
        docs = vectorstore.similarity_search(query, k=k)
        
        context = "\n\n".join([doc.page_content for doc in docs])
        return context