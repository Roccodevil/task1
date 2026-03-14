import os
import shutil

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

class VectorDBTool:
    def __init__(self, persist_directory="uploads/chroma_db"):
        # Chroma will create a database folder right inside your uploads directory
        self.persist_directory = persist_directory

        # Use your locally downloaded, CPU-friendly embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def store_document(self, text):
        """Chunks the text and stores it in a local Chroma database."""
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(text)

        # Optional: Clear the old database so agents don't get confused by old files
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)

        # Create the Chroma vector database and save it to your hard drive
        Chroma.from_texts(
            texts=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )

        return "Document successfully embedded and stored in LOCAL Chroma DB."

    def query_context(self, query, k=3):
        """Retrieves the most relevant chunks from the local Chroma database."""
        if not os.path.exists(self.persist_directory):
            return "Memory Error: No local document memory found."

        # Connect to the existing local database
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

        docs = vectorstore.similarity_search(query, k=k)

        context = "\n\n".join([doc.page_content for doc in docs])
        return context