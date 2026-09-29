import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

PERSIST_DIRECTORY = "./chroma_db"


def get_retriever():
  # Load the pre-built vector store directly
  vectorstore = Chroma(
      persist_directory=PERSIST_DIRECTORY, embedding_function=OpenAIEmbeddings()
  )
  return vectorstore.as_retriever()
  # Otherwise, load documents and build the vector store
  loader = DirectoryLoader(
      "./data/runbooks", glob="**/*.md", loader_cls=TextLoader
  )
  documents = loader.load()

  text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
  docs = text_splitter.split_documents(documents)

  vectorstore = Chroma.from_documents(
      documents=docs,
      embedding=OpenAIEmbeddings(),
      persist_directory=PERSIST_DIRECTORY,
  )

  return vectorstore.as_retriever()