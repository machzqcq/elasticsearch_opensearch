# Build and Ingest Meta Dictionary - AI-Powered Database Metadata Enhancement

> 🎯 **Objective**: Extract database metadata, enhance it with AI-generated descriptions, and ingest it into OpenSearch for semantic search capabilities

---

## 🏗️ High-Level Architecture

```mermaid
graph TB
    subgraph "🔧 Traditional Engineering"
        A[MSSQL Database<br/>AdventureWorks] -->|SQLAlchemy<br/>Connection| B[Database Connector]
        B -->|SQL Queries<br/>INFORMATION_SCHEMA| C[Metadata Extraction]
        C -->|pandas DataFrame| D[Data Cleaning &<br/>Sampling]
    end
    
    subgraph "🤖 AI Layer"
        D -->|Sample Values| E[DeepSeek API]
        E -->|LLM Inference| F[Column Descriptions]
        E -->|LLM Inference| G[Table Descriptions]
        F -->|Batch/Parallel| H[Optimized Processing]
        G -->|Sequential| H
    end
    
    subgraph "🔍 OpenSearch Platform"
        H -->|Enhanced Metadata| I[OpenSearch Cluster]
        I -->|Deploy Model| J[HuggingFace<br/>Sentence Transformer]
        J -->|Create Pipeline| K[Ingest Pipeline<br/>Auto-Embeddings]
        K -->|Bulk Ingestion| L[Vector Index<br/>768-dim embeddings]
        L -->|Query| M[Hybrid Search<br/>BM25 + k-NN]
    end
    
    style A fill:#e8f4f8,stroke:#0066cc,stroke-width:3px
    style E fill:#fff4e6,stroke:#ff9800,stroke-width:3px
    style I fill:#e8f5e9,stroke:#4caf50,stroke-width:3px
    style M fill:#f3e5f5,stroke:#9c27b0,stroke-width:3px
```

---

## 📊 Detailed Workflow

### Phase 1: Database Metadata Extraction (Traditional Engineering)

```mermaid
flowchart LR
    subgraph "🗄️ Source Database"
        DB[(MSSQL Server<br/>AdventureWorks)]
    end
    
    subgraph "🔌 Connection Layer"
        CONN[MSSQLConnector<br/>pymssql + SQLAlchemy]
    end
    
    subgraph "📋 Metadata Queries"
        Q1[INFORMATION_SCHEMA.TABLES<br/>Table Names, Schemas, Types]
        Q2[INFORMATION_SCHEMA.COLUMNS<br/>Column Names, Data Types, Nullability]
        Q3[Sample Data Queries<br/>TOP N random values per column]
    end
    
    subgraph "🧹 Data Processing"
        DF[pandas DataFrame<br/>Metadata Consolidation]
        FILTER[Schema Filtering<br/>Exclude: dbo, sys, etc.]
        SAMPLE[Data Sampling<br/>10 random values/column]
    end
    
    DB -->|Secure Connection| CONN
    CONN -->|Execute Queries| Q1
    CONN -->|Execute Queries| Q2
    CONN -->|Execute Queries| Q3
    Q1 --> DF
    Q2 --> DF
    Q3 --> SAMPLE
    DF --> FILTER
    FILTER --> SAMPLE
    
    style DB fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style CONN fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style DF fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
```

**Key Components:**
- 🔧 **Traditional Engineering**: Database connectivity, SQL queries, data extraction
- 📊 **Output**: Structured metadata with table/column information and sample values

---

### Phase 2: AI-Powered Description Generation (DeepSeek API)

```mermaid
flowchart TD
    subgraph "📥 Input Data"
        META[Metadata DataFrame<br/>+ Sample Values]
    end
    
    subgraph "🤖 AI Processing Strategies"
        META --> STRATEGY{Choose Strategy}
        
        STRATEGY -->|Sequential| SEQ[Original Method<br/>1 column = 1 API call<br/>⏱️ Slowest]
        STRATEGY -->|Batching| BATCH[Batch Processing<br/>5 columns = 1 API call<br/>⚡ 2-3x faster]
        STRATEGY -->|Parallel| PARA[Parallel Processing<br/>Multiple concurrent calls<br/>⚡ 2-3x faster]
        STRATEGY -->|Hybrid ⭐| HYBRID[Batch + Parallel<br/>Best of both worlds<br/>🚀 5-10x faster]
        
        SEQ --> API1[DeepSeek API]
        BATCH --> API2[DeepSeek API]
        PARA --> API3[DeepSeek API]
        HYBRID --> API4[DeepSeek API]
    end
    
    subgraph "🎯 AI Generation"
        API1 --> LLM1[LLM Inference<br/>deepseek-chat model]
        API2 --> LLM2[LLM Inference<br/>deepseek-chat model]
        API3 --> LLM3[LLM Inference<br/>deepseek-chat model]
        API4 --> LLM4[LLM Inference<br/>deepseek-chat model]
        
        LLM1 --> COL[Column Descriptions<br/>What does this column contain?]
        LLM2 --> COL
        LLM3 --> COL
        LLM4 --> COL
    end
    
    subgraph "📊 Table-Level Analysis"
        COL --> TAPI[DeepSeek API<br/>Table Context]
        TAPI --> TLLM[LLM Inference<br/>Table Purpose]
        TLLM --> TDESC[Table Descriptions<br/>What does this table store?]
    end
    
    subgraph "💾 Output"
        TDESC --> EXCEL[Enhanced Metadata<br/>Excel File]
        EXCEL --> COLS[INFERRED_COLUMN_DESCRIPTION<br/>INFERRED_TABLE_DESCRIPTION]
    end
    
    style META fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style HYBRID fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px,stroke-dasharray: 5 5
    style API4 fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style LLM4 fill:#ffccbc,stroke:#bf360c,stroke-width:2px
    style EXCEL fill:#e1bee7,stroke:#4a148c,stroke-width:2px
```

**Performance Optimization:**

| Strategy | API Calls | Processing Time | Speedup |
|----------|-----------|-----------------|---------|
| Sequential | 1 per column | ~10 min (100 cols) | 1x (baseline) |
| Batch | 1 per 5 columns | ~2-3 min | 2-3x faster |
| Parallel | Concurrent calls | ~2-3 min | 2-3x faster |
| **Hybrid ⭐** | **Batched + Parallel** | **~30-60 sec** | **5-10x faster** |

**Key Components:**
- 🤖 **AI Layer**: LLM-powered semantic understanding of data
- 💰 **Cost**: ~$0.05-0.10 for 100-200 columns (DeepSeek pricing)
- ⚡ **Recommended**: Hybrid strategy with `batch_size=3, max_workers=2`

---

### Phase 3: OpenSearch Ingestion Pipeline (ML + Vector Search)

```mermaid
flowchart TB
    subgraph "📦 Preparation"
        EXCEL[Enhanced Metadata<br/>Excel File]
        EXCEL --> READ[pandas read_excel<br/>Load DataFrame]
        READ --> FILTER[Filter & Clean<br/>Remove excluded schemas]
    end
    
    subgraph "🐳 OpenSearch Platform"
        DOCKER[Docker Compose<br/>OpenSearch Cluster]
        DOCKER --> CONN[Python Client<br/>opensearchpy]
        
        CONN --> ML{ML Commons<br/>Configuration}
        ML --> ALLOW[Allow ML on Data Nodes<br/>Set Memory Thresholds]
    end
    
    subgraph "🧠 ML Model Deployment"
        ALLOW --> REG[Register Model<br/>HuggingFace Repository]
        REG --> MODEL[msmarco-distilbert<br/>-base-tas-b<br/>768 dimensions]
        MODEL --> DEPLOY[Deploy Model<br/>TORCH_SCRIPT format]
        DEPLOY --> WAIT[Wait for DEPLOYED state<br/>max 5 minutes]
    end
    
    subgraph "⚙️ Ingest Pipeline"
        WAIT --> CREATE_PIPE[Create Ingest Pipeline<br/>text_embedding processor]
        CREATE_PIPE --> FIELD_MAP[Field Mapping<br/>text_field → text_field_embedding]
        FIELD_MAP --> PIPE_READY[Pipeline Ready<br/>Auto-generates embeddings]
    end
    
    subgraph "🗂️ Index Creation"
        FILTER --> MAP_GEN[Generate Mappings<br/>create_opensearch_mappings]
        MAP_GEN --> PROPS[Properties Definition<br/>Text + Vector fields]
        PROPS --> SETTINGS[Index Settings<br/>knn: true<br/>default_pipeline]
        PIPE_READY --> SETTINGS
        SETTINGS --> IDX_CREATE[Create Index<br/>adventure_works_meta_ai_ready]
    end
    
    subgraph "📤 Bulk Ingestion"
        IDX_CREATE --> BULK[Bulk Helper<br/>helpers.bulk]
        BULK --> DOC1[Document 1]
        BULK --> DOC2[Document 2]
        BULK --> DOC3[Document N]
        
        DOC1 --> PIPELINE1[Pipeline Processing]
        DOC2 --> PIPELINE2[Pipeline Processing]
        DOC3 --> PIPELINE3[Pipeline Processing]
        
        PIPELINE1 --> EMB1[Generate Embeddings<br/>768-dim vectors]
        PIPELINE2 --> EMB2[Generate Embeddings<br/>768-dim vectors]
        PIPELINE3 --> EMB3[Generate Embeddings<br/>768-dim vectors]
        
        EMB1 --> STORED1[Store Document<br/>+ Embeddings]
        EMB2 --> STORED2[Store Document<br/>+ Embeddings]
        EMB3 --> STORED3[Store Document<br/>+ Embeddings]
    end
    
    subgraph "✅ Verification"
        STORED1 --> VERIFY[Verify Ingestion<br/>Count & Sample Docs]
        STORED2 --> VERIFY
        STORED3 --> VERIFY
        VERIFY --> COMPLETE[✅ Index Ready<br/>for Semantic Search]
    end
    
    style DOCKER fill:#e3f2fd,stroke:#0277bd,stroke-width:3px
    style MODEL fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style PIPE_READY fill:#f1f8e9,stroke:#558b2f,stroke-width:2px
    style COMPLETE fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

**Key Features:**

1. **🧠 ML Model Integration**
   - Model: `sentence-transformers/msmarco-distilbert-base-tas-b`
   - Format: TORCH_SCRIPT (optimized for inference)
   - Dimensions: 768 (standard embedding size)
   - Deployment: Automatic with health checks

2. **⚙️ Ingest Pipeline**
   - **text_embedding processor**: Converts text → vectors
   - **Automatic processing**: Every document ingested gets embeddings
   - **Field mapping**: `TABLE_NAME` → `TABLE_NAME_embedding`
   - **No manual work**: Embeddings generated server-side

3. **🗂️ Index Configuration**
   - **k-NN enabled**: Supports vector similarity search
   - **HNSW algorithm**: Fast approximate nearest neighbor search
   - **L2 distance**: Euclidean distance for similarity
   - **Dual fields**: Original text + vector embeddings

---

### Phase 4: Hybrid Search (BM25 + k-NN)

```mermaid
flowchart LR
    subgraph "🔍 Query Input"
        Q[User Query<br/>'Store']
    end
    
    subgraph "🔀 Dual Search Path"
        Q --> PATH1{Parallel Execution}
        Q --> PATH2{Parallel Execution}
        
        PATH1 --> BM25[Keyword Search<br/>BM25 Algorithm]
        PATH2 --> KNN[Semantic Search<br/>k-NN + Embeddings]
        
        BM25 --> MATCH[Match Query<br/>TABLE_NAME: 'Store']
        KNN --> NEURAL[Neural Query<br/>TABLE_NAME_embedding]
        
        MATCH --> SCORE1[Relevance Score<br/>Keyword Boost: 1.0]
        NEURAL --> EMBED[Generate Query Embedding<br/>768-dim vector]
        EMBED --> SCORE2[Similarity Score<br/>Semantic Boost: 1.0]
    end
    
    subgraph "🎯 Score Combination"
        SCORE1 --> COMBINE[Bool Should Query<br/>minimum_should_match: 1]
        SCORE2 --> COMBINE
        COMBINE --> RANK[Combined Ranking<br/>BM25 + k-NN scores]
    end
    
    subgraph "📊 Results"
        RANK --> TOP[Top K Results<br/>Sorted by score]
        TOP --> R1[Result 1<br/>Sales.Store.BusinessEntityID<br/>Score: 2.94]
        TOP --> R2[Result 2<br/>Sales.Store.Name<br/>Score: 2.94]
        TOP --> R3[Result 3<br/>Sales.Store.SalesPersonID<br/>Score: 2.94]
    end
    
    subgraph "🔧 Field Filtering"
        R1 --> EXCLUDE[Exclude Embeddings<br/>_source: excludes *_embedding]
        R2 --> EXCLUDE
        R3 --> EXCLUDE
        EXCLUDE --> DISPLAY[Display Results<br/>Schema, Table, Column, Description]
    end
    
    style Q fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style BM25 fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    style KNN fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    style COMBINE fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
    style DISPLAY fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

**Hybrid Search Benefits:**

| Feature | Keyword Search (BM25) | Semantic Search (k-NN) | Hybrid Search |
|---------|----------------------|------------------------|---------------|
| **Exact Matches** | ✅ Excellent | ❌ May miss | ✅ Best of both |
| **Synonyms** | ❌ Misses | ✅ Understands | ✅ Handles both |
| **Typos** | ❌ Sensitive | ✅ Tolerant | ✅ Robust |
| **Context** | ❌ Limited | ✅ Strong | ✅ Comprehensive |
| **Speed** | 🚀 Very fast | ⚡ Fast | ⚡ Fast |

---

## 🎨 Technology Stack

```mermaid
mindmap
  root((Meta Dictionary<br/>System))
    🔧 Traditional Engineering
      Database
        MSSQL Server
        SQLAlchemy
        pymssql
      Data Processing
        pandas
        numpy
        Excel export
      Sampling
        SQL TOP N
        NEWID random
    🤖 AI Components
      LLM Provider
        DeepSeek API
        deepseek-chat model
      Optimization
        Batch processing
        Parallel execution
        Concurrent futures
      Cost Management
        Schema filtering
        Smart sampling
        Token limits
    🔍 OpenSearch Platform
      Deployment
        Docker Compose
        Cluster setup
        Security config
      ML Commons
        Model registration
        HuggingFace integration
        TORCH_SCRIPT deployment
      Indexing
        Ingest pipelines
        Auto-embeddings
        Bulk ingestion
      Search
        BM25 keyword
        k-NN semantic
        Hybrid scoring
    📊 Data Flow
      Extract
        Metadata queries
        Sample data
      Transform
        AI descriptions
        Data cleaning
      Load
        Vector embeddings
        OpenSearch index
```

---

## 📈 Performance Metrics

### AI Processing Performance

```mermaid
gantt
    title Processing Time Comparison (100 columns)
    dateFormat X
    axisFormat %s

    section Sequential
    Original Method : 0, 600s
    
    section Batch
    Batch Processing : 0, 180s
    
    section Parallel
    Parallel Execution : 0, 180s
    
    section Hybrid
    Optimized Hybrid : 0, 45s
```

### Cost Analysis

```mermaid
pie title "Total Cost Breakdown (100 columns)"
    "DeepSeek API Calls" : 85
    "OpenSearch Compute" : 10
    "Data Transfer" : 5
```

**Estimated Costs:**
- 💰 **DeepSeek API**: ~$0.05-0.10 for 100-200 columns
- 🔧 **OpenSearch**: Free (local Docker) or ~$0.01/hour (cloud)
- 📊 **Total**: Under $0.15 for complete pipeline

---

## 🎯 Key Features Summary

### Where Traditional Engineering is Used
- ✅ **Database connectivity**: SQLAlchemy, pymssql
- ✅ **Metadata extraction**: SQL queries, INFORMATION_SCHEMA
- ✅ **Data manipulation**: pandas DataFrame operations
- ✅ **Sampling logic**: Random selection, TOP N queries
- ✅ **Excel export**: openpyxl, structured output
- ✅ **Bulk ingestion**: Batch processing, error handling

### Where AI is Used
- 🤖 **Column descriptions**: LLM inference on sample data
- 🤖 **Table descriptions**: LLM inference on table structure
- 🤖 **Semantic understanding**: Context-aware descriptions
- 🤖 **Batch optimization**: Smart batching for efficiency
- 🤖 **Natural language**: Human-readable descriptions

### Where OpenSearch Platform is Used
- 🔍 **Index creation**: Dynamic mapping generation
- 🔍 **ML model deployment**: HuggingFace integration
- 🔍 **Ingest pipeline**: Automatic embedding generation
- 🔍 **Vector storage**: 768-dimensional embeddings
- 🔍 **Hybrid search**: BM25 + k-NN combination
- 🔍 **Score normalization**: Combined relevance ranking
- 🔍 **Field filtering**: Exclude embeddings from results

---

## 🚀 Quick Start Commands

```bash
# 1. Start OpenSearch cluster
cd opensearch-RAG
docker compose -f docker-compose-fully-optimized.yml up -d

# 2. Install dependencies
pip install opensearchpy opensearch-py-ml pandas openpyxl requests

# 3. Run the notebook
jupyter notebook build_meta_dictionary.ipynb

# 4. Key parameters to tune
SAMPLING_COUNT = 10              # Samples per column
batch_size = 3                   # Columns per API batch
max_workers = 2                  # Parallel workers
```

---

## 📚 References

- **OpenSearch**: [opensearch.org](https://opensearch.org)
- **DeepSeek API**: [platform.deepseek.com](https://platform.deepseek.com)
- **HuggingFace Models**: [huggingface.co/sentence-transformers](https://huggingface.co/sentence-transformers)
- **k-NN Plugin**: [OpenSearch k-NN Documentation](https://opensearch.org/docs/latest/search-plugins/knn/)

---

## 🎓 Learning Outcomes

After implementing this pipeline, you will understand:

1. ✅ **Database metadata extraction** using SQL and Python
2. ✅ **LLM integration** for semantic enrichment
3. ✅ **Performance optimization** with batching and parallelization
4. ✅ **Vector embeddings** and semantic search concepts
5. ✅ **OpenSearch ML Commons** for model deployment
6. ✅ **Ingest pipelines** for automated processing
7. ✅ **Hybrid search** combining keyword and semantic approaches
8. ✅ **Production-ready patterns** for scalable AI applications

---

**🎉 Result**: A fully functional AI-powered metadata search system that combines traditional engineering excellence with modern AI capabilities, all built on the robust OpenSearch platform!
