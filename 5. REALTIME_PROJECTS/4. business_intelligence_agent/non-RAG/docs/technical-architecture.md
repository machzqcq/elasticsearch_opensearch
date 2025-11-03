# 🔧 Text-to-SQL Agent - Technical Architecture

## System Architecture Overview

```mermaid
graph TB
    subgraph "🖥️ User Interface Layer"
        UI[Jupyter Notebook Interface<br/>ipywidgets]
        Input[Natural Language Input]
        Display[Results Display]
    end
    
    subgraph "🤖 LLM Provider Layer"
        LLM[Universal LLM Provider]
        OpenAI[OpenAI GPT<br/>gpt-4o/gpt-4o-mini]
        Anthropic[Anthropic Claude<br/>claude-3.5-sonnet]
        Google[Google Gemini<br/>gemini-1.5-flash]
        DeepSeek[DeepSeek<br/>deepseek-chat]
    end
    
    subgraph "🧠 SQL Generation Layer"
        Analyzer[Query Analyzer]
        Generator[SQL Generator]
        Cleaner[Response Cleaner]
        Metadata[Metadata Context]
    end
    
    subgraph "🛡️ Safety & Validation Layer"
        Guard[Safety Guard]
        Validator[Syntax Validator]
        Limiter[Row/Timeout Limiter]
    end
    
    subgraph "🗄️ Database Layer"
        Connector[MSSQL Connector<br/>pymssql + SQLAlchemy]
        MetaExtractor[Metadata Extractor]
        Executor[SQL Executor]
    end
    
    subgraph "📊 Analytics Layer"
        VizEngine[Visualization Engine<br/>matplotlib/seaborn/plotly]
        InsightGen[AI Insight Generator]
        Monitor[Execution Monitor]
        History[Query History Logger]
    end
    
    UI --> Input
    Input --> LLM
    LLM --> OpenAI & Anthropic & Google & DeepSeek
    LLM --> Analyzer
    Analyzer --> Metadata
    Analyzer --> Generator
    Generator --> Cleaner
    Cleaner --> Guard
    Guard --> Validator
    Validator --> Limiter
    Limiter --> Executor
    Executor --> Connector
    Connector --> Display
    Display --> VizEngine
    Display --> InsightGen
    Executor --> Monitor
    Monitor --> History
    Connector --> MetaExtractor
    MetaExtractor --> Metadata
    
    style UI fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    style LLM fill:#f3e5f5,stroke:#6a1b9a,stroke-width:3px
    style Guard fill:#ffebee,stroke:#c62828,stroke-width:3px
    style Connector fill:#fff3e0,stroke:#e65100,stroke-width:3px
    style VizEngine fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

---

## 🔄 Detailed Component Flow

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant UI as UI Layer
    participant LLM as LLM Provider
    participant SQLGen as SQL Generator
    participant Safety as Safety Layer
    participant DB as Database
    participant Viz as Visualization
    participant Monitor as Monitoring
    
    User->>UI: Enter natural language query
    UI->>SQLGen: Request analysis
    SQLGen->>DB: Fetch metadata
    DB-->>SQLGen: Return schema info
    
    SQLGen->>LLM: Analyze query + metadata
    LLM-->>SQLGen: Return relevant tables/columns
    
    SQLGen->>LLM: Generate SQL query
    LLM-->>SQLGen: Return raw SQL
    SQLGen->>SQLGen: Clean & format SQL
    
    SQLGen-->>UI: Display generated SQL
    
    User->>UI: Execute SQL
    UI->>Safety: Validate query
    
    alt Query is Unsafe
        Safety-->>UI: Reject with reason
        UI-->>User: Show error message
    else Query is Safe
        Safety->>DB: Execute query
        DB->>Monitor: Log execution start
        
        alt Query Succeeds
            DB-->>Monitor: Log success + metrics
            DB-->>UI: Return results DataFrame
            Monitor->>Monitor: Calculate stats
            UI-->>User: Display results table
            
            opt User requests visualization
                User->>Viz: Create charts
                Viz->>Viz: Detect data types
                Viz->>Viz: Generate appropriate plots
                Viz-->>User: Display visualizations
            end
            
            opt User requests insights
                User->>LLM: Generate insights
                LLM-->>User: Return AI analysis
            end
        else Query Fails
            DB-->>Monitor: Log failure + error
            Monitor->>Monitor: Analyze error pattern
            Monitor-->>UI: Suggest fixes
            UI-->>User: Show error + suggestions
        end
    end
    
    Monitor->>Monitor: Update statistics
```

---

## 🏗️ Class Architecture

```mermaid
classDiagram
    class MSSQLConnector {
        -server: str
        -database: str
        -username: str
        -password: str
        -port: int
        -engine: Engine
        +create_connection_string()
        +connect() bool
        +execute_query(query, params) DataFrame
        +get_tables() DataFrame
        +get_columns() DataFrame
    }
    
    class DatabaseMetadataExtractor {
        -db_connector: MSSQLConnector
        -metadata_df: DataFrame
        +extract_full_metadata() DataFrame
        -_infer_column_description() str
        +save_to_excel(filename) bool
    }
    
    class UniversalLLMProvider {
        -providers_config: dict
        +query_openai(prompt, api_key, model) str
        +query_anthropic(prompt, api_key, model) str
        +query_google_gemini(prompt, api_key, model) str
        +query_deepseek(prompt, api_key, model) str
        +query_llm(prompt, provider, model) str
    }
    
    class SQLGenerator {
        -metadata_df: DataFrame
        -llm_provider: UniversalLLMProvider
        +analyze_query_requirements(query, provider, model) str
        +generate_sql_query(query, analysis, provider, model) str
        -_prepare_metadata_context() str
        -_clean_sql_response(response) str
        +process_nl_query(query, provider, model) tuple
    }
    
    class SQLExecutor {
        -db_connector: MSSQLConnector
        -execution_history: list
        +execute_sql_query(query, timeout, max_rows) DataFrame
        -_is_safe_query(query) bool
        -_suggest_error_fixes(error_msg)
        -_log_execution(query, rows, time, success, error)
        +get_execution_history() DataFrame
        +get_query_statistics()
    }
    
    class DataVisualizationAndInsights {
        -llm_provider: UniversalLLMProvider
        +generate_insights(df, query, provider, model) str
        -_prepare_data_summary(df) str
        +create_visualizations(df, query)
        -_create_distribution_plots(df, cols)
        -_create_categorical_plots(df, cols)
        -_create_correlation_heatmap(df, cols)
        -_create_time_series_plots(df, date_col, num_cols)
        -_create_top_n_analysis(df, cat_col, num_col)
        -_create_interactive_plot(df, num_cols, cat_cols)
    }
    
    class InteractiveTextToSQL {
        -sql_generator: SQLGenerator
        -sql_executor: SQLExecutor
        -llm_provider: UniversalLLMProvider
        -viz_insights: DataVisualizationAndInsights
        -last_result_df: DataFrame
        +setup_widgets()
        +generate_sql(button)
        +execute_sql(button)
        +create_visualizations(button)
        +generate_insights(button)
        +display_interface()
    }
    
    MSSQLConnector <-- DatabaseMetadataExtractor
    MSSQLConnector <-- SQLExecutor
    UniversalLLMProvider <-- SQLGenerator
    UniversalLLMProvider <-- DataVisualizationAndInsights
    SQLGenerator <-- InteractiveTextToSQL
    SQLExecutor <-- InteractiveTextToSQL
    UniversalLLMProvider <-- InteractiveTextToSQL
    DataVisualizationAndInsights <-- InteractiveTextToSQL
    DatabaseMetadataExtractor ..> SQLGenerator : provides metadata
```

---

## 🛡️ Safety & Guardrails Implementation

```mermaid
flowchart TD
    Query[📝 SQL Query Input] --> Parse{🔍 Parse Query}
    
    Parse --> CheckKeywords[Check for Dangerous Keywords]
    CheckKeywords --> Keywords{Contains:<br/>DROP/DELETE/UPDATE/EXEC/etc?}
    
    Keywords -->|Yes| Block1[❌ Block Query]
    Keywords -->|No| CheckStart[Check Query Start]
    
    CheckStart --> Start{Starts with<br/>SELECT or WITH?}
    Start -->|No| Block2[❌ Only SELECT Allowed]
    Start -->|Yes| SetTimeout[⏱️ Set Query Timeout<br/>Default: 30s]
    
    SetTimeout --> SetLimit[📊 Set Row Limit<br/>Default: 10,000 rows]
    SetLimit --> Execute[✅ Execute Query]
    
    Execute --> Monitor{⏱️ Monitor<br/>Execution}
    
    Monitor -->|Timeout| Abort[⏹️ Abort Query]
    Monitor -->|Success| CheckRows{📊 Check<br/>Row Count}
    
    CheckRows -->|> Max Rows| Truncate[✂️ Truncate Results]
    CheckRows -->|<= Max Rows| Return[✅ Return Full Results]
    
    Truncate --> Log[📝 Log Execution]
    Return --> Log
    Abort --> LogError[📝 Log Error]
    Block1 --> LogError
    Block2 --> LogError
    
    Log --> Stats[📊 Update Statistics]
    LogError --> Stats
    
    Stats --> Done([End])
    
    style Block1 fill:#ffebee,stroke:#c62828,stroke-width:3px
    style Block2 fill:#ffebee,stroke:#c62828,stroke-width:3px
    style Abort fill:#ffccbc,stroke:#d84315,stroke-width:2px
    style Execute fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style Return fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
```

---

## 📊 Monitoring & Logging System

```mermaid
graph TB
    subgraph "📝 Execution Logging"
        Start[Query Execution Start] --> RecordStart[Record Timestamp]
        RecordStart --> RecordQuery[Store Query Text]
        RecordQuery --> Track[Track Execution]
    end
    
    subgraph "⏱️ Performance Metrics"
        Track --> Time[Measure Execution Time]
        Track --> Rows[Count Rows Returned]
        Track --> Status[Record Success/Failure]
    end
    
    subgraph "❌ Error Handling"
        Status -->|Failure| CaptureError[Capture Error Message]
        CaptureError --> Categorize[Categorize Error Type]
        Categorize --> GenSuggestions[Generate Fix Suggestions]
    end
    
    subgraph "📊 Statistics Database"
        Time --> AvgCalc[Calculate Average Time]
        Rows --> TotalCalc[Calculate Total Rows]
        Status --> RateCalc[Calculate Success Rate]
        GenSuggestions --> ErrorDB[Store Error Patterns]
    end
    
    subgraph "📈 Analytics Dashboard"
        AvgCalc --> Trend1[Performance Trends]
        TotalCalc --> Trend2[Usage Patterns]
        RateCalc --> Trend3[Quality Metrics]
        ErrorDB --> Trend4[Common Issues]
    end
    
    Trend1 --> Report[📄 Analytics Report]
    Trend2 --> Report
    Trend3 --> Report
    Trend4 --> Report
    
    style Start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style CaptureError fill:#ffebee,stroke:#c62828,stroke-width:2px
    style Report fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

---

## 🎨 Visualization Pipeline

```mermaid
flowchart LR
    subgraph "📊 Input Processing"
        Data[Query Results<br/>DataFrame] --> Analyze[Analyze Data Types]
        Analyze --> Numeric[Numeric Columns]
        Analyze --> Categorical[Categorical Columns]
        Analyze --> DateTime[DateTime Columns]
    end
    
    subgraph "🎨 Visualization Selection"
        Numeric --> V1[Distribution Plots<br/>matplotlib/seaborn]
        Numeric --> V2[Correlation Heatmap<br/>seaborn]
        
        Categorical --> V3[Bar Charts<br/>seaborn]
        
        DateTime --> V4[Time Series<br/>matplotlib]
        
        Numeric & Categorical --> V5[Top N Analysis<br/>matplotlib]
        Numeric & Categorical --> V6[Interactive Plots<br/>plotly]
    end
    
    subgraph "📈 Output Generation"
        V1 --> Output[Display Visualizations]
        V2 --> Output
        V3 --> Output
        V4 --> Output
        V5 --> Output
        V6 --> Output
    end
    
    style Data fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Analyze fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Output fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

---

## 🔐 Security Architecture

```mermaid
graph TB
    subgraph "🔑 Authentication Layer"
        EnvVars[Environment Variables<br/>.env file]
        APIKeys[LLM API Keys]
        DBCreds[Database Credentials]
    end
    
    subgraph "🛡️ Query Security"
        Whitelist[SELECT Whitelist]
        Blacklist[Dangerous Keyword Blacklist]
        Sanitize[Input Sanitization]
    end
    
    subgraph "⚡ Resource Protection"
        Timeout[Query Timeout Limits]
        RowLimit[Row Count Limits]
        RateLimit[API Rate Limiting]
    end
    
    subgraph "📝 Audit Trail"
        Logger[Query Logger]
        ErrorLog[Error Logger]
        AccessLog[Access Logger]
    end
    
    EnvVars --> APIKeys & DBCreds
    APIKeys --> RateLimit
    DBCreds --> Sanitize
    
    Whitelist --> Sanitize
    Blacklist --> Sanitize
    
    Sanitize --> Timeout
    Timeout --> RowLimit
    
    RowLimit --> Logger
    Logger --> ErrorLog
    ErrorLog --> AccessLog
    
    style EnvVars fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Whitelist fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style Blacklist fill:#ffebee,stroke:#c62828,stroke-width:2px
    style AccessLog fill:#fff3e0,stroke:#e65100,stroke-width:2px
```

---

## 🔄 Data Flow Architecture

```mermaid
graph LR
    subgraph "Input"
        NL[Natural Language<br/>Query]
    end
    
    subgraph "Processing Pipeline"
        direction TB
        P1[1. Load Metadata<br/>from Excel/DB] --> P2[2. Analyze Query<br/>LLM API Call]
        P2 --> P3[3. Generate SQL<br/>LLM API Call]
        P3 --> P4[4. Clean SQL<br/>Regex/String Processing]
        P4 --> P5[5. Validate Safety<br/>Pattern Matching]
        P5 --> P6[6. Execute Query<br/>pymssql + SQLAlchemy]
        P6 --> P7[7. Process Results<br/>pandas DataFrame]
    end
    
    subgraph "Optional Analytics"
        direction TB
        A1[Visualizations<br/>matplotlib/seaborn/plotly]
        A2[AI Insights<br/>LLM API Call]
    end
    
    subgraph "Output"
        Results[Results + Charts<br/>+ Insights]
    end
    
    NL --> P1
    P7 --> A1 & A2
    A1 --> Results
    A2 --> Results
    P7 --> Results
    
    style NL fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style P5 fill:#ffebee,stroke:#c62828,stroke-width:2px
    style P6 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Results fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

---

## 📦 Technology Stack

```mermaid
mindmap
  root((🚀 Tech Stack))
    🐍 Core Python
      pandas::Data manipulation
      numpy::Numerical computing
      sqlalchemy::ORM & DB abstraction
      pymssql::MSSQL driver
    🎨 Visualization
      matplotlib::Static plots
      seaborn::Statistical viz
      plotly::Interactive charts
    🤖 LLM Integration
      requests::HTTP API calls
      OpenAI API::GPT models
      Anthropic API::Claude models
      Google API::Gemini models
      DeepSeek API::DeepSeek models
    🖥️ UI Components
      ipywidgets::Interactive widgets
      IPython.display::Rich output
    📊 Data Export
      openpyxl::Excel files
      python-dotenv::Env management
    🛡️ Safety
      re::Regex validation
      text::SQL parameterization
```

---

## 🔧 Configuration Management

```mermaid
flowchart TD
    Start([Application Start]) --> LoadEnv[Load .env File]
    
    LoadEnv --> CheckDB{Database<br/>Config Present?}
    CheckDB -->|No| Error1[❌ Warn: Missing DB Config]
    CheckDB -->|Yes| ValidateDB[Validate DB Connection]
    
    LoadEnv --> CheckLLM{LLM API<br/>Keys Present?}
    CheckLLM -->|None| Error2[❌ Warn: No LLM Keys]
    CheckLLM -->|At least one| ValidateLLM[Validate API Keys]
    
    ValidateDB -->|Success| DBReady[✅ DB Ready]
    ValidateDB -->|Failure| DBError[❌ DB Connection Failed]
    
    ValidateLLM -->|Success| LLMReady[✅ LLM Ready]
    ValidateLLM -->|Failure| LLMError[❌ Invalid API Key]
    
    DBReady --> Extract[Extract Metadata]
    Extract --> Cache[Cache to Excel]
    
    DBReady & LLMReady --> SystemReady[🚀 System Ready]
    
    Error1 & Error2 & DBError & LLMError --> Partial[⚠️ Partial Functionality]
    
    SystemReady --> Interface[Display Interface]
    Partial --> Interface
    
    style Start fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style Error1 fill:#ffebee,stroke:#c62828,stroke-width:2px
    style Error2 fill:#ffebee,stroke:#c62828,stroke-width:2px
    style SystemReady fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

---

## 📈 Performance Optimization Strategies

```mermaid
graph TB
    subgraph "🗄️ Database Layer"
        D1[Metadata Caching<br/>Excel/Memory]
        D2[Connection Pooling<br/>SQLAlchemy]
        D3[Query Parameterization<br/>Prevent SQL Injection]
    end
    
    subgraph "🤖 LLM Layer"
        L1[Response Caching<br/>Avoid Duplicate Calls]
        L2[Temperature=0.1<br/>Consistent Results]
        L3[Token Limits<br/>Cost Control]
    end
    
    subgraph "📊 Data Processing"
        P1[Row Limiting<br/>Memory Management]
        P2[Lazy Loading<br/>Large DataFrames]
        P3[Type Optimization<br/>pandas dtypes]
    end
    
    subgraph "🎨 Visualization"
        V1[Sample Large Datasets<br/>Plot Performance]
        V2[SVG for Static<br/>WebGL for Interactive]
        V3[Lazy Rendering<br/>On-Demand Charts]
    end
    
    D1 & D2 & D3 --> Perf1[⚡ Fast Queries]
    L1 & L2 & L3 --> Perf2[💰 Cost Efficient]
    P1 & P2 & P3 --> Perf3[🚀 Quick Processing]
    V1 & V2 & V3 --> Perf4[🎯 Smooth UX]
    
    Perf1 & Perf2 & Perf3 & Perf4 --> Optimal[✨ Optimal Performance]
    
    style Optimal fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

---

## 🧪 Testing & Quality Assurance

```mermaid
flowchart TB
    subgraph "🔍 Input Validation"
        T1[Query Structure Tests]
        T2[SQL Injection Tests]
        T3[Metadata Validation]
    end
    
    subgraph "🛡️ Safety Tests"
        S1[Dangerous Keyword Detection]
        S2[Timeout Enforcement]
        S3[Row Limit Verification]
    end
    
    subgraph "📊 Functional Tests"
        F1[SQL Generation Accuracy]
        F2[Query Execution]
        F3[Visualization Generation]
        F4[Insight Quality]
    end
    
    subgraph "⚡ Performance Tests"
        P1[Response Time < 5s]
        P2[Memory Usage < 1GB]
        P3[API Call Efficiency]
    end
    
    T1 & T2 & T3 --> Pass1{All Pass?}
    S1 & S2 & S3 --> Pass2{All Pass?}
    F1 & F2 & F3 & F4 --> Pass3{All Pass?}
    P1 & P2 & P3 --> Pass4{All Pass?}
    
    Pass1 & Pass2 & Pass3 & Pass4 -->|Yes| Deploy[✅ Ready for Production]
    Pass1 & Pass2 & Pass3 & Pass4 -->|No| Fix[❌ Fix Issues]
    
    Fix --> T1
    
    style Deploy fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    style Fix fill:#ffebee,stroke:#c62828,stroke-width:2px
```

---

## 🚀 Deployment Architecture

```mermaid
graph TB
    subgraph "📦 Package Dependencies"
        Core[Python 3.8+]
        DB[pymssql<br/>sqlalchemy]
        Viz[matplotlib<br/>seaborn<br/>plotly]
        UI[ipywidgets<br/>jupyter]
        Utils[pandas<br/>openpyxl<br/>python-dotenv]
    end
    
    subgraph "🔧 Environment Setup"
        Env[.env Configuration]
        Secrets[API Keys<br/>DB Credentials]
    end
    
    subgraph "🗄️ Database Setup"
        MSSQL[SQL Server Instance]
        Meta[Metadata Extraction]
        Perms[User Permissions]
    end
    
    subgraph "🤖 LLM Setup"
        Keys[API Key Registration]
        Provider[Provider Selection]
        Test[API Connectivity Test]
    end
    
    subgraph "🚀 Application"
        Notebook[Jupyter Notebook]
        Interface[Interactive UI]
        Monitor[Monitoring Dashboard]
    end
    
    Core --> Notebook
    DB & Viz & UI & Utils --> Notebook
    Env --> Secrets
    Secrets --> Notebook
    MSSQL --> Meta
    Meta --> Notebook
    Perms --> MSSQL
    Keys --> Provider
    Provider --> Test
    Test --> Notebook
    Notebook --> Interface
    Interface --> Monitor
    
    style Notebook fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    style Interface fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

---

## 🔄 Error Recovery Flow

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Generating: User submits query
    Generating --> Validating: SQL generated
    Validating --> Executing: Query safe
    Validating --> Error: Query unsafe
    Executing --> Success: Query successful
    Executing --> Error: Query failed
    
    Error --> Analyzing: Analyze error type
    Analyzing --> Suggesting: Generate suggestions
    Suggesting --> Retry: User modifies query
    Retry --> Generating
    
    Success --> Visualizing: User requests viz
    Success --> Insights: User requests insights
    Success --> Idle: Done
    
    Visualizing --> Idle: Charts displayed
    Insights --> Idle: Analysis shown
    
    Error --> Idle: User cancels
    
    note right of Error
        Logged to history
        Statistics updated
    end note
    
    note right of Success
        Logged to history
        Stats updated
        Results cached
    end note
```

---

## 🏗️ Production-Ready Features Summary

### 🛡️ Safety & Security
- **Query Validation**: Blocks dangerous operations (DROP, DELETE, UPDATE, EXEC)
- **Parameterization**: Prevents SQL injection attacks
- **Timeout Protection**: Prevents long-running queries
- **Row Limits**: Controls memory usage and response size
- **Error Handling**: Graceful degradation with helpful messages

### 📊 Monitoring & Observability
- **Execution Logging**: Complete audit trail of all queries
- **Performance Metrics**: Execution time, row counts, success rates
- **Error Analytics**: Pattern detection and categorization
- **Statistics Dashboard**: Real-time query performance insights
- **History Tracking**: Query history with full context

### 🎨 User Experience
- **Multi-LLM Support**: Flexibility across providers
- **Auto-Visualization**: Intelligent chart selection
- **AI Insights**: Business-friendly analysis
- **Interactive UI**: Easy-to-use widgets
- **Error Guidance**: Helpful fix suggestions

### ⚡ Performance
- **Metadata Caching**: Reduces database calls
- **Connection Pooling**: Efficient resource usage
- **Lazy Loading**: Memory optimization
- **Response Caching**: Reduced LLM API calls
- **Optimized Rendering**: Fast visualization display

### 🔧 Maintainability
- **Modular Design**: Separated concerns, easy to extend
- **Configuration Management**: Environment-based setup
- **Comprehensive Logging**: Debug-friendly output
- **Type Hints**: Better code documentation
- **Clean Architecture**: SOLID principles applied
