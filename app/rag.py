import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define paths
RUNBOOKS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/runbooks")
)
DB_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/chroma_db")
)


def get_vector_store():
  """Loads markdown runbooks, chunks them, embeds them locally using Ollama

  (nomic-embed-text), and stores them in a local Chroma vector store.
  """
  # 1. Initialize local embeddings using Ollama and nomic-embed-text
  embeddings = OllamaEmbeddings(model="nomic-embed-text")

  # 2. Check if vector store already exists; if so, load it
  if os.path.exists(DB_DIR) and os.listdir(DB_DIR):
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

  # 3. Load markdown documents from the runbooks directory
  loader = DirectoryLoader(
      RUNBOOKS_DIR, glob="**/*.md", loader_cls=TextLoader, show_progress=True
  )
  docs = loader.load()

  if not docs:
    raise ValueError(
        f"No runbooks found in {RUNBOOKS_DIR}. Please add markdown files."
    )

  # 4. Split documents into smaller chunks for precise retrieval
  text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=500, chunk_overlap=50
  )
  split_docs = text_splitter.split_documents(docs)

  # 5. Create and persist the vector store
  vector_store = Chroma.from_documents(
      documents=split_docs, embedding=embeddings, persist_directory=DB_DIR
  )

  return vector_store


def get_retriever():
  """Returns a retriever object to query the runbook database."""
  store = get_vector_store()
  return store.as_retriever(
      search_type="similarity", search_kwargs={"k": 2}
  )


if __name__ == "__main__":
  print("Initializing local vector store with nomic-embed-text...")
  retriever = get_retriever()
  results = retriever.invoke("How do I fix database connection timeout?")
  print(f"\nRetrieved {len(results)} relevant runbook chunks:")
  for i, doc in enumerate(results):
    print(f"\n--- Chunk {i+1} ---\n{doc.page_content}")