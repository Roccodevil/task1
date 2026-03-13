from crewai import Agent

from models.ollama_client import get_local_llm


def create_data_agent():
	"""Instantiates the agent responsible for summarizing raw parsed data."""
	local_llm = get_local_llm("llama3")

	return Agent(
		role='Senior Data Extraction Specialist',
		goal='Summarize the document structure to give the Explainer Agent a high-level map of the data.',
		backstory='You structure complex text and VLM-extracted visual descriptions into clean summaries.',
		verbose=True,
		allow_delegation=False,
		llm=local_llm
	)
