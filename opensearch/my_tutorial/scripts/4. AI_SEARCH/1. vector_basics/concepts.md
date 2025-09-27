# Concepts

This page defines key terms and techniques related to vector search in OpenSearch.

## Vector representations

**Vector embeddings** are numerical representations of data—such as text, images, or audio—that encode meaning or features into a high-dimensional space. These embeddings enable similarity-based comparisons for search and machine learning (ML) tasks.

**Dense vectors** are high-dimensional numerical representations where most elements have nonzero values. They are typically produced by deep learning models and are used in semantic search and ML applications.

**Sparse vectors** contain mostly zero values and are often used in techniques like neural sparse search to efficiently represent and retrieve information.

## Vector search fundamentals

**Vector search**, also known as similarity search or nearest neighbor search, is a technique for finding items that are most similar to a given input vector. It is widely used in applications such as recommendation systems, image retrieval, and natural language processing.

A **space** defines how similarity or distance between two vectors is measured. Different spaces use different distance metrics, such as Euclidean distance or cosine similarity, to determine how closely vectors resemble each other.

A **method** refers to the algorithm used to organize vector data during indexing and retrieve relevant results during search in approximate k-NN search. Different methods balance trade-offs between accuracy, speed, and memory usage.

An **engine** is the underlying library that implements vector search methods. It determines how vectors are indexed, stored, and retrieved during similarity search operations.

## k-NN search

**k-nearest neighbors (k-NN) search** finds the k most similar vectors to a given query vector in an index. The similarity is determined based on a specified distance metric.

**Exact k-NN search** performs a brute-force comparison between a query vector and all vectors in an index, computing the exact nearest neighbors. This approach provides high accuracy but can be computationally expensive for large datasets.

**Approximate k-NN search** reduces computational complexity by using indexing techniques that speed up search operations while maintaining high accuracy. These methods restructure the index or reduce the dimensionality of vectors to improve performance.

## Query types

A **k-NN query** searches vector fields using a query vector.

A **neural query** searches vector fields using text or image data.

A **neural sparse query** searches vector fields using raw text or sparse vector tokens.

## Search techniques

**Semantic search** interprets the intent and contextual meaning of a query rather than relying solely on exact keyword matches. This approach improves the relevance of search results, especially for natural language queries.

**Hybrid search** combines lexical (keyword-based) search with semantic (vector-based) search to improve search relevance. This approach ensures that results include both exact keyword matches and conceptually similar content.

**Multimodal search** enables you to search across multiple types of data, such as text and images. It allows queries in one format (for example, text) to retrieve results in another (for example, images).

**Radial search** retrieves all vectors within a specified distance or similarity threshold from a query vector. It is useful for tasks that require finding all relevant matches within a given range rather than retrieving a fixed number of nearest neighbors.

**Neural sparse search** uses an inverted index, similar to BM25, to efficiently retrieve relevant documents based on sparse vector representations. This approach maintains the efficiency of traditional lexical search while incorporating semantic understanding.

**Conversational search** allows you to interact with a search system using natural language queries and refine results through follow-up questions. This approach enhances the user experience by making search more intuitive and interactive.

**Retrieval-augmented generation (RAG)** enhances large language models (LLMs) by retrieving relevant information from an index and incorporating it into the model's response. This approach improves the accuracy and relevance of generated text.

## Indexing and storage techniques

**Text chunking** involves splitting long documents or text passages into smaller segments to improve search retrieval and relevance. Chunking helps vector search models process large amounts of text more effectively.

**Vector quantization** is a technique for reducing the storage size of vector embeddings by approximating them using a smaller set of representative vectors. This process enables efficient storage and retrieval in large-scale vector search applications.

**Scalar quantization (SQ)** reduces vector precision by mapping floating-point values to a limited set of discrete values, decreasing memory requirements while preserving search accuracy.

**Product quantization (PQ)** divides high-dimensional vectors into smaller subspaces and quantizes each subspace separately, enabling efficient approximate nearest neighbor search with reduced memory usage.

**Binary quantization** compresses vector representations by converting numerical values to binary formats. This technique reduces storage requirements and accelerates similarity computations.

**Disk-based vector search** stores vector embeddings on disk rather than in memory, using binary quantization to reduce memory consumption while maintaining search efficiency.