 # Tool for building documentation for github repositories
from langchain_community.document_loaders import ReadTheDocsLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
# Wrapper for pinecone to make integration (but separated from Pinecone)
from langchain_pinecone import PineconeVectorStore
import os
from dotenv import load_dotenv

def ingest_docs() -> None:
    """Function which uses executes ReadTheDocsLoader on a directory containing html files representing documentation of repositories, chunks it and stores it into Pinecone Vector Store.
    """
    docs_folder = "docs"
    downloaded_docs_path_list = os.path.dirname(os.environ.get("DOCUMENTATION_URL").replace("https://", "")).split("/")

    docs_path = os.path.join(os.getcwd(), docs_folder, *downloaded_docs_path_list)
    print(docs_path)
    # Load from downloaded html docs,may take sometime due to large amount of documents
    loader = ReadTheDocsLoader(
        path=docs_path,
        encoding="utf-8"
    )
    raw_documents = loader.load()
    print(f"Loaded {len(raw_documents)} documents")

    # Reduce chunks hence also embeddings for persistence
    text_splitter =  RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 100,
        separators= ["\n\n", "\n", " ", ""]
    )

    #Splut documents
    documents = text_splitter.split_documents(documents=raw_documents)
    print(f"Splitted into {len(documents)} chunks")

    # Dictionary replacement to Replace source path with original path by modifying path name and updating the doc source value and then inserting the updated docs. Will need asyncio to do concurency indexing
    for doc in documents:
        old_path = doc.metadata["source"]
        # Replace our folder name with https: and switch \ to / (Windows path) so that we can refer back to actual web urls correctly.
        new_url = old_path.replace(docs_folder, "https:/").replace("\\", "/")
        original_url = ''.join(["https:", new_url.split("https:")[-1]])
        print(f"Updating url: {original_url}")
        doc.metadata.update({"source": original_url})
    print(f"Inserting {len(documents)} to Pinecone")
    
    # Define embeddings with OpenAI text-embedding-3-large
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    # Ingest into Pinecone vector store
    PineconeVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        index_name=os.environ.get("PINECONE_INDEX")
    )
    print("****Loading to vectorstore done ***")

if __name__ == "__main__":
    load_dotenv()
    ingest_docs()