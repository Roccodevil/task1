from crewai import LLM

def get_local_llm(model_name="llama3"):
    """
    Initializes the local Ollama CPU instance using CrewAI's native LLM class.
    Make sure you have run 'ollama run llama3' in your terminal before starting the app!
    """
    return LLM(
        model=f"ollama/{model_name}",
        base_url="http://localhost:11434" # Default Ollama local port
    )