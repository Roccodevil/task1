from crewai import Agent
from crewai.tools import tool

from models.ollama_client import get_local_llm
from tools.vector_db import VectorDBTool
from tools.web_search import WebSearchTool

vector_db = VectorDBTool()
web_search = WebSearchTool()


@tool("Search Internet")
def search_internet(query: str) -> str:
	"""Search the internet for missing context or definitions using Tavily."""
	return web_search.search(query)


@tool("Query Local Document Memory")
def query_memory(query: str) -> str:
	"""Query the local Chroma document memory to retrieve specific details from the uploaded document."""
	return vector_db.query_context(query)


def create_explainer_agent():
	"""Instantiates the agent responsible for XAI and answering user doubts."""
	local_llm = get_local_llm("llama3")

	return Agent(
		role='Lead AI Explainer & XAI Specialist',
		goal='Explain complex data systematically, addressing user doubts using Chain-of-Thought reasoning.',
		backstory='You break down technical documents. You actively use your tools to recall facts from the document memory or search the internet if context is missing.',
		verbose=True,
		allow_delegation=False,
		tools=[query_memory, search_internet],
		llm=local_llm
	)
