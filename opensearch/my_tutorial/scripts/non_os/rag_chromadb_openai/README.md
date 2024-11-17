# RAG process
Langchain example - https://python.langchain.com/docs/tutorials/rag/

## Indexing

- **Load**: First we need to load our data. This is done with Document Loaders.
- **Split**: Text splitters break large Documents into smaller chunks. This is useful both for indexing data and passing it into a model, as large chunks are harder to search over and won't fit in a model's finite context window.
- **Store**: We need somewhere to store and index our splits, so that they can be searched over later. This is often done using a VectorStore and Embeddings model.  
![alt text](rag_indexing.png)

## Retrieval and generation

- **Retrieve**: Given a user input, relevant splits are retrieved from storage using a Retriever.
- **Generate**: A ChatModel / LLM produces an answer using a prompt that includes both the question with the retrieved data  

![alt text](rag_retrieval_generation.png)


## Process Flow
- User Query enters the system
- Retriever processes query and searches Knowledge Base
- Relevant information retrieved from Knowledge Base
- Retrieved information combined with original query
- Prompt engineered with query and context
- Prompt sent to Large Language Model
- LLM generates response using prompt
- Generated response returned to user



## Overall Steps
- Install required libraries
- Set OpenAI API key
- Load document file
- Split text into chunks
- Initialize ChromaDB client
- Create a collection
- Create embeddings function
- Add documents to collection
- Define query function
- Query ChromaDB collection
- Generate response with OpenAI
- Print response output

## Explanation
- We start by loading a document and splitting it into manageable chunks
- We then create embeddings for these chunks using OpenAI's embedding model and store them in a ChromaDB collection
- The query_and_generate function performs two main tasks:
    - It queries the ChromaDB collection to retrieve relevant document chunks based on the input query
    - It uses OpenAI's language model to generate a response based on the retrieved context and the original query
