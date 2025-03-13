from haystack import Pipeline
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.components.generators import AzureOpenAIGenerator
from haystack.dataclasses import Document
from haystack.utils import Secret
from dotenv import load_dotenv
import os
import json

# Lade die Umgebungsvariablen aus der .env Datei
load_dotenv()

# Hole die Azure OpenAI Konfiguration aus den Umgebungsvariablen
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")

# Erstelle einen einfachen Dokumentenspeicher für den Retriever
documents = [
    Document(
        content="Haystack ist ein Open-Source-Framework für die Erstellung von NLP-Anwendungen."
    ),
    Document(
        content="Azure OpenAI Service bietet leistungsstarke Sprachmodelle für verschiedene Anwendungsfälle."
    ),
    Document(
        content="Python ist eine vielseitige Programmiersprache, die für KI und maschinelles Lernen beliebt ist."
    ),
]

# Initialisiere den Retriever
retriever = InMemoryBM25Retriever(documents=documents)

# Initialisiere den Azure OpenAI Generator
generator = AzureOpenAIGenerator(
    api_key=Secret.from_token(azure_api_key),
    azure_endpoint=azure_endpoint,
    azure_deployment=azure_deployment,
    api_version=azure_api_version,
    generation_kwargs={
        "response_format": {"type": "json_object"}  # Erzwinge JSON-Antworten
    },
)

# Erstelle eine Pipeline, die den Retriever und Generator verbindet
pipeline = Pipeline()
pipeline.add_component("retriever", retriever)
pipeline.add_component("generator", generator)

# Verbinde die Komponenten
pipeline.connect("retriever", "generator")


def query_llm(question):
    """
    Funktion zum Abfragen des LLMs mit einer Frage.

    Args:
        question (str): Die Frage an das LLM

    Returns:
        dict: Die Antwort des LLMs als JSON
    """
    # System-Prompt, der eine strukturierte JSON-Antwort erzwingt
    system_prompt = """
    Du bist ein hilfreicher Assistent, der Fragen beantwortet.
    Deine Antworten müssen immer im JSON-Format mit den folgenden Feldern sein:
    {
        "answer": "Deine Antwort auf die Frage",
        "confidence": Eine Zahl zwischen 0 und 1, die deine Zuversicht in die Antwort angibt,
        "sources": Ein Array von Quellen, die du verwendet hast (kann leer sein)
    }
    """

    # Führe die Pipeline aus
    result = pipeline.run(
        {
            "retriever": {"query": question},
            "generator": {
                "generation_kwargs": {
                    "system": system_prompt,
                    "response_format": {"type": "json_object"},
                }
            },
        }
    )

    # Extrahiere die JSON-Antwort
    try:
        # Da die Antwort bereits im JSON-Format ist (als String), parsen wir sie
        response_json = json.loads(result["generator"]["replies"][0])
        return response_json
    except json.JSONDecodeError:
        # Fallback, falls keine valide JSON zurückkommt
        return {
            "answer": result["generator"]["replies"][0],
            "confidence": 0.0,
            "sources": [],
        }


# Beispiel für die Verwendung
if __name__ == "__main__":
    # Beispielfrage
    question = "Was ist Haystack?"

    # Frage an das LLM stellen
    response = query_llm(question)

    # Ausgabe der Antwort
    print(json.dumps(response, indent=2, ensure_ascii=False))
