import os

from crewai import LLM

def get_local_llm(model_name="llama3"):
    """
    Initializes the local Ollama CPU instance using CrewAI's native LLM class.
    Make sure you have run 'ollama run llama3' in your terminal before starting the app!
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    return LLM(
        model=f"ollama/{model_name}",
        base_url=base_url
    )