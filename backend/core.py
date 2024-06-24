# Script to retrieve documents from vector store
import os
from dotenv import load_dotenv
from typing import Any, Tuple, List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# Wrapper for pinecone to make integration (but separated from Pinecone)
from langchain_pinecone import PineconeVectorStore
#from langchain.chains.retrieval_qa.base.RetrievalQA
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain

def run_llm(query:str, chat_history: List[Tuple[str,Any]]) -> Any:
    """Function which retrieves a RetreivalQA Chain completion based on PineconeVector store documents and query input fed. 
    
    ChatOpenAI is used as LLM model for LangChain's RetrievalQA and OpenAIEmbeddings is used to defined the embedding required by PineconeVectorStore with index_name referencing to PINECONE_INDEX variable of .env file. 

    Args:
        query (str): Input prompt to be fed into Retrieval QA

    Returns:
        Any: Retrieval QA Chain Completion based on the model used.
    """
    # Define embedding to be used (also used for indexing doc chunks)
    embeddings = OpenAIEmbeddings(
        api_key=os.environ.get("OPENAI_API_KEY"),
        model="text-embedding-3-large",
    )
    # Document source
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=os.environ.get("PINECONE_INDEX"),
        embedding=embeddings
    )
    #LLM
    llm = ChatOpenAI(verbose=True, temperature=0, model="gpt-3.5-turbo")
    # Use RetrievalChain with .from_chain for simple RAG on document without conversation
    
    # qa = RetrievalQA.from_chain_type(
    #     llm=llm,
    #     chain_type="stuff",
    #     retriever=docsearch.as_retriever(),
    #     return_source_documents = True,
    # )
    #return qa.invoke({"query": query)

    #Use ConversationalRetrievalChain with .from_llm (only method) when you need to infuse chat history to allow followup question. Assumes history is finite and wont exceed llm prompt tokens, otherwise care must be taken. Idea is it is augmenting the prompt sent to LLM with chat history as follows as per documentation.

    #"""Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
    # Chat History:
    # {chat_history}
    # Follow Up Input: {question}
    # Standalone question:"""
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=docsearch.as_retriever(),
        return_source_documents =True,
        verbose=True
    )

    return qa.invoke({"question": query, "chat_history": chat_history})


if __name__ == "__main__":
    # Call our function
    response = run_llm(query="What is RetrievalQA chain?")
    print(response)