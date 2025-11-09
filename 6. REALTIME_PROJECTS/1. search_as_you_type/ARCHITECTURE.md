# Architecture Diagrams for Search-as-you-Type Application

This document contains Mermaid diagrams explaining the architecture and workflows of the search-as-you-type application for both business and technical audiences.

## 1. Business User Workflow - High-Level Overview

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#667eea','primaryTextColor':'#fff','primaryBorderColor':'#764ba2','lineColor':'#764ba2','secondaryColor':'#e8eaf6','tertiaryColor':'#fff','background':'#f5f5f5','mainBkg':'#667eea','secondBkg':'#e8eaf6','border1':'#764ba2','border2':'#9575cd'}}}%%
graph TB
    Start([👤 User Opens App]) --> ChooseFrontend{Choose Interface}
    
    ChooseFrontend -->|Option 1| Streamlit[🎨 Streamlit App<br/>Python-based UI]
    ChooseFrontend -->|Option 2| Gradio[🎨 Gradio App<br/>ML-friendly UI]
    ChooseFrontend -->|Option 3| React[🎨 React App<br/>Modern Web UI]
    
    Streamlit --> EnterQuery[✍️ Type Search Query<br/>e.g., 'boots', 'shirt']
    Gradio --> EnterQuery
    React --> EnterQuery
    
    EnterQuery --> SelectFields[⚙️ Select Search Fields<br/>Product Name, Category, Manufacturer]
    
    SelectFields --> RealTimeSearch[⚡ Real-time Search<br/>Results appear as you type]
    
    RealTimeSearch --> ViewResults[📊 View Results]
    
    ViewResults --> ResultDetails[See Product Details:<br/>✓ Product Name<br/>✓ Category<br/>✓ Manufacturer<br/>✓ Price<br/>✓ Relevance Score]
    
    ResultDetails --> Decision{Satisfied?}
    
    Decision -->|No| RefineSearch[🔄 Refine Search Query]
    RefineSearch --> EnterQuery
    
    Decision -->|Yes| End([✅ Product Found!])
    
    style Start fill:#667eea,stroke:#764ba2,stroke-width:3px,color:#fff
    style End fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:#fff
    style EnterQuery fill:#fff3cd,stroke:#ff9800,stroke-width:2px
    style ViewResults fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style RealTimeSearch fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
```

## 2. Technical Architecture - System Components

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#1976d2','primaryTextColor':'#fff','primaryBorderColor':'#0d47a1','lineColor':'#1976d2','secondaryColor':'#bbdefb','tertiaryColor':'#fff'}}}%%
graph TB
    subgraph Frontend["🎨 Frontend Layer (Multiple Options)"]
        direction TB
        UI1[Streamlit App<br/>Port: 8501<br/>Python-based]
        UI2[Gradio App<br/>Port: 7860<br/>ML-friendly]
        UI3[React App<br/>Port: 3000<br/>Modern SPA]
    end
    
    subgraph Backend["⚙️ Backend Layer"]
        direction TB
        API[FastAPI Server<br/>Port: 8000<br/>RESTful API]
        
        subgraph Endpoints["API Endpoints"]
            E1[POST /api/search<br/>Main search endpoint]
            E2[POST /api/suggestions<br/>Autocomplete]
            E3[GET /api/health<br/>Health check]
        end
    end
    
    subgraph DataLayer["💾 Data Layer"]
        direction TB
        OSClient[OpenSearch Client<br/>Python SDK]
        
        subgraph SearchOps["Search Operations"]
            OP1[Phrase Prefix Match<br/>Autocomplete]
            OP2[Fuzzy Match<br/>Typo tolerance]
            OP3[Phrase Match<br/>Exact phrases]
        end
    end
    
    subgraph Storage["🗄️ Storage Layer"]
        OS[(OpenSearch Cluster<br/>Port: 9200<br/>Index: ecommerce)]
        
        subgraph IndexData["Index Data"]
            D1[Product Names]
            D2[Categories]
            D3[Manufacturers]
            D4[Prices & Metadata]
        end
    end
    
    UI1 -.->|HTTP/REST| API
    UI2 -.->|HTTP/REST| API
    UI3 -.->|HTTP/REST| API
    
    API --> E1
    API --> E2
    API --> E3
    
    E1 --> OSClient
    E2 --> OSClient
    E3 --> OSClient
    
    OSClient --> OP1
    OSClient --> OP2
    OSClient --> OP3
    
    OP1 -.->|Query DSL| OS
    OP2 -.->|Query DSL| OS
    OP3 -.->|Query DSL| OS
    
    OS --> D1
    OS --> D2
    OS --> D3
    OS --> D4
    
    style Frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style Backend fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style DataLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    style Storage fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

## 3. Search Flow - Technical Deep Dive

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#00897b','primaryTextColor':'#fff','primaryBorderColor':'#004d40','lineColor':'#00897b','secondaryColor':'#b2dfdb','tertiaryColor':'#fff'}}}%%
sequenceDiagram
    autonumber
    participant U as 👤 User
    participant FE as 🎨 Frontend<br/>(Streamlit/Gradio/React)
    participant API as ⚙️ FastAPI Backend
    participant OS as 💾 OpenSearch Client
    participant DB as 🗄️ OpenSearch Cluster
    
    Note over U,DB: User Initiates Search
    
    U->>FE: Types "boot" in search box
    FE->>FE: Validates input
    
    Note over FE,API: REST API Call
    FE->>+API: POST /api/search<br/>{query: "boot", fields: [...]}
    
    Note over API,OS: Backend Processing
    API->>API: Validate request
    API->>+OS: search_as_you_type()
    
    Note over OS,DB: Multi-Strategy Query
    OS->>OS: Build bool query with:<br/>1. Phrase prefix<br/>2. Fuzzy match<br/>3. Phrase match
    
    OS->>+DB: Execute search query
    DB->>DB: Score documents
    DB->>DB: Apply highlighting
    DB-->>-OS: Return results + metadata
    
    Note over OS,API: Result Processing
    OS-->>-API: Raw search results
    API->>API: Transform results<br/>Extract highlights<br/>Format response
    
    Note over API,FE: Response Delivery
    API-->>-FE: JSON response<br/>{total, took, hits[]}
    
    Note over FE,U: UI Update
    FE->>FE: Parse results<br/>Apply highlighting<br/>Render UI
    FE-->>U: Display matching products
    
    Note over U,DB: User sees results in ~100ms
    
    rect rgb(200, 230, 200)
        Note right of DB: Search Features:<br/>✓ Phrase Prefix (autocomplete)<br/>✓ Fuzzy Match (typo tolerance)<br/>✓ Phrase Match (exact search)<br/>✓ Field boosting<br/>✓ Highlighting
    end
```

## 4. Data Flow Architecture

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#d32f2f','primaryTextColor':'#fff','primaryBorderColor':'#b71c1c','lineColor':'#d32f2f','secondaryColor':'#ffcdd2','tertiaryColor':'#fff'}}}%%
flowchart LR
    subgraph Input["📥 Input Layer"]
        direction TB
        Q[User Query:<br/>'shirt']
        F[Selected Fields:<br/>• product_name<br/>• category<br/>• manufacturer]
        C[Config:<br/>size: 10<br/>from: 0]
    end
    
    subgraph Processing["⚙️ Processing Layer"]
        direction TB
        V[Validation]
        QB[Query Builder]
        
        subgraph QTypes["Query Types"]
            Q1[Phrase Prefix<br/>boost: 2.0]
            Q2[Best Fields<br/>fuzziness: AUTO]
            Q3[Phrase Match<br/>slop: 2, boost: 1.5]
        end
        
        E[Execute Search]
    end
    
    subgraph Transform["🔄 Transformation Layer"]
        direction TB
        R[Raw Results]
        H[Apply Highlights]
        S[Score Sorting]
        P[Pagination]
    end
    
    subgraph Output["📤 Output Layer"]
        direction TB
        J[JSON Response:<br/>• total count<br/>• execution time<br/>• hits array<br/>• highlights]
        D[Display in UI:<br/>• Product cards<br/>• Highlighted text<br/>• Relevance scores]
    end
    
    Q --> V
    F --> V
    C --> V
    
    V --> QB
    QB --> Q1
    QB --> Q2
    QB --> Q3
    
    Q1 --> E
    Q2 --> E
    Q3 --> E
    
    E --> R
    R --> H
    H --> S
    S --> P
    
    P --> J
    J --> D
    
    style Input fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Processing fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style Transform fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style Output fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
```

## 5. Deployment Architecture

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#5e35b1','primaryTextColor':'#fff','primaryBorderColor':'#4527a0','lineColor':'#5e35b1','secondaryColor':'#d1c4e9','tertiaryColor':'#fff'}}}%%
graph TB
    subgraph DevEnv["💻 Development Environment"]
        direction TB
        Dev[Developer Machine]
        UV[uv Package Manager]
        Git[Git Repository]
    end
    
    subgraph AppServers["🚀 Application Servers"]
        direction TB
        
        subgraph Frontend["Frontend Servers"]
            ST[Streamlit<br/>:8501]
            GR[Gradio<br/>:7860]
            RE[React<br/>:3000]
        end
        
        subgraph Backend["Backend Server"]
            FA[FastAPI<br/>:8000<br/>Uvicorn ASGI]
        end
    end
    
    subgraph DataServices["💾 Data Services"]
        direction TB
        OSC[OpenSearch Cluster<br/>:9200<br/>https://]
        
        subgraph Indices["Indices"]
            EC[ecommerce index<br/>9000+ documents]
        end
        
        subgraph Features["Features Enabled"]
            F1[Full-text search]
            F2[Phrase matching]
            F3[Fuzzy search]
            F4[Highlighting]
        end
    end
    
    subgraph Monitoring["📊 Monitoring"]
        direction TB
        H[Health Checks<br/>/api/health]
        L[Logs<br/>Application logs]
        M[Metrics<br/>Response times]
    end
    
    Dev --> UV
    UV -.->|Install dependencies| Git
    Git -.->|Deploy| AppServers
    
    ST -->|HTTP REST| FA
    GR -->|HTTP REST| FA
    RE -->|HTTP REST| FA
    
    FA -->|OpenSearch Protocol| OSC
    
    OSC --> EC
    EC --> F1
    EC --> F2
    EC --> F3
    EC --> F4
    
    FA --> H
    FA --> L
    FA --> M
    
    style DevEnv fill:#e0f7fa,stroke:#006064,stroke-width:2px
    style AppServers fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style DataServices fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style Monitoring fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
```

## 6. Component Interaction Matrix

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#00695c','primaryTextColor':'#fff','primaryBorderColor':'#004d40','lineColor':'#00695c','secondaryColor':'#b2dfdb','tertiaryColor':'#fff'}}}%%
flowchart TD
    subgraph Users["👥 User Types"]
        BU[Business User<br/>Focus: Products & Results]
        TU[Technical User<br/>Focus: Architecture & Performance]
    end
    
    subgraph Interfaces["🎨 User Interfaces"]
        ST[Streamlit<br/>• Simple Python UI<br/>• Quick prototyping<br/>• Data science friendly]
        GR[Gradio<br/>• ML model demos<br/>• Easy sharing<br/>• Interactive widgets]
        RE[React<br/>• Modern web app<br/>• Responsive design<br/>• Production-ready]
    end
    
    subgraph Core["⚙️ Core Backend"]
        API[FastAPI<br/>• RESTful endpoints<br/>• Auto documentation<br/>• Type validation<br/>• CORS enabled]
    end
    
    subgraph Search["🔍 Search Engine"]
        OS[OpenSearch<br/>• Distributed search<br/>• Real-time indexing<br/>• Complex queries<br/>• Scalable]
    end
    
    subgraph Features["✨ Key Features"]
        AC[Autocomplete<br/>phrase_prefix]
        FM[Fuzzy Matching<br/>typo tolerance]
        PM[Phrase Matching<br/>exact search]
        HL[Highlighting<br/>matched terms]
    end
    
    BU -.->|Uses| ST
    BU -.->|Uses| GR
    BU -.->|Uses| RE
    TU -.->|Configures| API
    TU -.->|Manages| OS
    
    ST -->|HTTP| API
    GR -->|HTTP| API
    RE -->|HTTP| API
    
    API -->|Search Queries| OS
    
    OS --> AC
    OS --> FM
    OS --> PM
    OS --> HL
    
    style Users fill:#ffebee,stroke:#c62828,stroke-width:2px
    style Interfaces fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Core fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style Search fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Features fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
```

---

## Diagram Usage Guide

### For Business Users:
- **Diagram 1**: Understand the user journey and how to use the application
- **Diagram 6**: See how different components serve your needs

### For Technical Users:
- **Diagram 2**: Understand system architecture and components
- **Diagram 3**: Deep dive into the search flow
- **Diagram 4**: Data transformation pipeline
- **Diagram 5**: Deployment architecture and infrastructure

### For Project Managers:
- **Diagram 1**: User experience flow
- **Diagram 5**: Infrastructure requirements
- **Diagram 6**: Technology stack overview
