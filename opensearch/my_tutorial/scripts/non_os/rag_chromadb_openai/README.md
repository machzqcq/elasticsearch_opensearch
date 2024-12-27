# RAG process
Langchain example - https://python.langchain.com/docs/tutorials/rag/

# Need for RAG
RAG (Retrieval-Augmented Generation) is necessary despite the capabilities of large language models (LLMs) because it addresses several critical limitations of LLMs:

-  **Limitations**: LLMs can only store a fixed amount of information in their parameters. They lack access to dynamic, up-to-date, or domain-specific data that may not have been part of their training.

- **Reducing Hallucination**: LLMs often "hallucinate" or generate plausible but inaccurate or made-up information. RAG grounds their responses in factual data from external sources, improving accuracy.

- **Keeping Information Current**: Unlike LLMs, which have a fixed training cutoff, RAG systems can retrieve and use the latest information from external databases or APIs.

- **Efficient Use of Resources**: Instead of retraining or fine-tuning LLMs on large datasets for every specific domain or update, RAG uses retrieval mechanisms to augment responses, saving time and computational resources.

- **Scalability for Specialized Use Cases**: RAG enables LLMs to perform better in specialized domains (e.g., legal, healthcare) by leveraging targeted knowledge bases, making them more versatile for real-world applications.

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
