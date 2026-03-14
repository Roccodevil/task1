from crewai import Crew, Process, Task

from agents.data_agent import create_data_agent
from agents.explainer_agent import create_explainer_agent
from tools.document_parser import DocumentParser
from tools.vector_db import VectorDBTool

doc_parser = DocumentParser()


def run_explainer_crew(filepath, user_doubt, vector_db_path):
    print("Starting data parsing pipeline...")

    raw_extracted_data = doc_parser.parse_file(filepath)

    print("Storing extracted context in local Chroma DB...")
    vector_db = VectorDBTool(persist_directory=vector_db_path)
    vector_db.store_document(raw_extracted_data)

    data_agent = create_data_agent()
    explainer_agent = create_explainer_agent(vector_db)

    extract_task = Task(
        description=f'Review this raw data snapshot and create a high-level summary of what the document contains: \n\n{raw_extracted_data[:3000]}...',
        expected_output='A clean, structured summary map of the document contents.',
        agent=data_agent
    )

    explain_task = Task(
        description=f'Explain the document systematically. The user has a specific doubt: "{user_doubt}". \n\nCRITICAL: You must use the "Query Local Document Memory" tool to retrieve the exact data needed to answer this doubt. If you still lack context, use the "Search Internet" tool. Apply Chain-of-Thought reasoning to explain your steps clearly.',
        expected_output='A complete, step-by-step explanation answering the user doubt with facts pulled directly from the tools.',
        agent=explainer_agent
    )

    document_crew = Crew(
        agents=[data_agent, explainer_agent],
        tasks=[extract_task, explain_task],
        process=Process.sequential,
        verbose=True
    )

    return document_crew.kickoff()