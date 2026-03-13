import os

from tavily import TavilyClient


class WebSearchTool:
	@staticmethod
	def search(query):
		"""Searches the web using Tavily for up-to-date context."""
		api_key = os.getenv("TAVILY_API_KEY")
		if not api_key:
			return "Error: Tavily API key not found. Cannot perform web search."

		try:
			client = TavilyClient(api_key=api_key)
			response = client.search(query=query, search_depth="basic", max_results=3)

			results_text = "Web Search Results:\n"
			for result in response.get('results', []):
				results_text += f"- {result['title']}: {result['content']}\n"

			return results_text
		except Exception as e:
			return f"Web search failed: {str(e)}"
