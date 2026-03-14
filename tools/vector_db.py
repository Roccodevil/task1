import os
import shutil
import gc

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

        # For request-scoped paths this is mostly a safety guard.
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)

        os.makedirs(self.persist_directory, exist_ok=True)

        # Create the Chroma vector database and save it to your hard drive
        vectorstore = Chroma.from_texts(
            texts=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )

        # Release local references promptly to reduce SQLite lock windows.
        del vectorstore
        gc.collect()

        return "Document successfully embedded and stored in LOCAL Chroma DB."

    def query_context(self, query, k=3):
        """Retrieves the most relevant chunks from the local Chroma database."""
        if not os.path.exists(self.persist_directory):
            return "Memory Error: No local document memory found."

        # Connect to the existing local database
        vectorstore = None
        try:
            vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )

            docs = vectorstore.similarity_search(query, k=k)
            context = "\n\n".join([doc.page_content for doc in docs])
            return context
        finally:
            if vectorstore is not None:
                del vectorstore
            gc.collect()