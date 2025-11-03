# Data Prepper Log Ingestion Demo Guide

```mermaid
graph LR
    A["🐍 Apache Log Generator<br/><br/>apache-fake-log-gen.py<br/>Generates fake logs<br/>to test.log"] -->|Writes logs| B["📄 Log File<br/><br/>test.log<br/>Mounted as volume"]
    
    B -->|Tails logs| C["🔄 Fluent Bit<br/><br/>fluent-bit.conf<br/>Reads & forwards logs"]
    
    C -->|HTTP POST to /log/ingest<br/>Port 2021| D["⚙️ Data Prepper<br/><br/>log_pipeline.yaml<br/>HTTP Source"]
    
    D -->|Grok Parsing<br/>COMMONAPACHELOG| E["🔧 Grok Processor<br/><br/>Parses structured logs<br/>Extracts fields"]
    
    E -->|Sends logs| F["🔐 OpenSearch Sink<br/><br/>opensearch:9200<br/>Index: apache_logs"]
    
    F -->|Visualized in| G["📊 OpenSearch Dashboards<br/><br/>http://localhost:5601<br/>Query & analyze logs"]
    
    style A fill:#FF6B6B,stroke:#C92A2A,color:#fff,stroke-width:3px
    style B fill:#4ECDC4,stroke:#0B7285,color:#fff,stroke-width:2px
    style C fill:#45B7D1,stroke:#0C3B66,color:#fff,stroke-width:3px
    style D fill:#FFA502,stroke:#D97706,color:#fff,stroke-width:3px
    style E fill:#95E1D3,stroke:#38B000,color:#000,stroke-width:2px
    style F fill:#667BC6,stroke:#2D3561,color:#fff,stroke-width:3px
    style G fill:#DA70D6,stroke:#9D1EA8,color:#fff,stroke-width:3px
```

This is a guide that will walk users through setting up a sample Data Prepper pipeline for log ingestion. 
This guide will go through the steps required to create a simple log ingestion pipeline from \
Fluent Bit → Data Prepper → OpenSearch. This log ingestion flow is shown in the diagram above.

## Understanding the Components in the OpenSearch Ecosystem

### 1. Fluent Bit: Lightweight Data Collection Agent

#### What is Fluent Bit?

Fluent Bit is a lightweight, open-source data shipper and log processor. It's designed to collect logs from various sources, process them, and forward them to multiple destinations with minimal memory and CPU footprint.

#### Key Capabilities

- **Log Tailing**: Monitors files and collects new log entries as they're written (like monitoring `/var/log/test.log` in this example)
- **Multiple Inputs**: Can collect logs from files, syslog, Windows Event Logs, network sockets, and more
- **Data Transformation**: Basic data filtering, enrichment, and format conversion
- **Multiple Outputs**: Forward logs to Data Prepper, Elasticsearch, Splunk, CloudWatch, HTTP endpoints, etc.
- **Low Overhead**: Extremely lightweight (~7MB memory footprint), ideal for edge devices and production environments
- **Configuration**: Simple INI-style configuration files for quick setup

#### When to Use Fluent Bit

- **Log Collection from File Systems**: Monitoring application logs, system logs, and custom log files
- **Edge Computing**: Collecting telemetry on IoT devices or edge servers with limited resources
- **Streaming Data**: Real-time monitoring of log files with minimal latency
- **Multi-Destination Routing**: Collecting logs from one source and sending to multiple systems
- **Volume Ingestion**: High-volume log collection when resource efficiency matters

#### Use Case in This Project

In our log ingestion example, Fluent Bit:
1. **Tails** the `test.log` file for new log entries
2. **Reads** each new Apache log line as it's written
3. **Forwards** the raw log data via HTTP POST to Data Prepper's HTTP endpoint on port 2021

```conf
# From fluent-bit.conf
[INPUT]
  name tail              # Monitors file for new entries
  path /var/log/test.log # The file to tail

[OUTPUT]
  Name http              # Send via HTTP
  Host data-prepper      # Send to Data Prepper container
  Port 2021             # Data Prepper's default port
  URI /log/ingest       # Data Prepper's HTTP source endpoint
```

---

### 2. Data Prepper: Log Processing Pipeline Engine

#### What is Data Prepper?

Data Prepper is an OpenSearch-native, server-side data ingestion and processing service. It's designed specifically for the OpenSearch ecosystem and allows you to define complex pipelines that receive, process, and output data in a scalable manner.

#### Key Capabilities

- **Multiple Sources**: HTTP, OTel (OpenTelemetry), S3, and other input plugins
- **Advanced Processing**: Transform data using multiple processors (Grok, Lambda, Mutate, Date, GeoIP, Service Map, etc.)
- **Flexible Routing**: Route different log types to different sinks
- **Scalability**: Designed for high-throughput production environments
- **Stateless Design**: Can be horizontally scaled across multiple instances
- **OpenSearch Integration**: Native support for OpenSearch as a sink with automatic index management

#### When to Use Data Prepper

- **Complex Log Processing Pipelines**: When you need multi-step processing (parse → enrich → filter → index)
- **Structured Data Extraction**: Parsing unstructured logs into structured fields
- **OpenSearch-Specific Workflows**: When you want tight integration with OpenSearch features
- **Production Deployments**: High-volume, mission-critical log ingestion at scale
- **Monitoring & Observability**: Full data observability with service maps and trace data
- **Conditional Logic**: Route different events to different indices based on content

#### Use Case in This Project

In our log ingestion example, Data Prepper:
1. **Receives** HTTP POST requests from Fluent Bit at `/log/ingest`
2. **Processes** the raw Apache logs through a Grok processor
3. **Sends** structured, parsed logs to OpenSearch for indexing

```yaml
# From log_pipeline.yaml
log-pipeline:
  source:
    http:                    # Receive data via HTTP
      ssl: false
  processor:
    - grok:                  # Apply Grok parsing
        match:
          log: [ "%{COMMONAPACHELOG}" ]
  sink:
    - opensearch:            # Send to OpenSearch
        hosts: [ "https://opensearch:9200" ]
        index: apache_logs    # Into this index
```

---

### 3. Grok Processor: Structured Data Extraction

#### What is Grok?

Grok is a pattern-matching language built on regular expressions. It allows you to parse unstructured text logs into structured fields without writing complex regex patterns manually. Grok uses predefined patterns (like `%{IP}`, `%{TIMESTAMP}`, `%{HTTPMETHOD}`) that can be combined into complex patterns.

#### Key Capabilities

- **Pattern Library**: 100+ built-in patterns for common log formats
- **Pattern Composition**: Combine patterns to match complex log structures
- **Named Captures**: Extract data into named fields automatically
- **Data Type Conversion**: Convert extracted values to appropriate types (int, float, boolean, etc.)
- **Custom Patterns**: Define your own patterns for custom log formats
- **Performance**: Highly optimized pattern matching engine

#### Common Grok Patterns

```
%{IP}              # IP addresses (e.g., 192.168.1.1)
%{TIMESTAMP_ISO8601}  # ISO 8601 timestamps
%{HTTPMETHOD}      # HTTP methods (GET, POST, PUT, DELETE)
%{NUMBER}          # Numeric values
%{WORD}            # Single words
%{QUOTEDSTRING}    # Quoted strings
%{COMMONAPACHELOG} # Complete Apache Common Log format
```

#### When to Use Grok Processor

- **Apache/Nginx Logs**: Parse web server logs with predefined patterns
- **Application Logs**: Extract fields from application-generated logs
- **Syslog Parsing**: Parse system logs with structured format
- **Custom Log Formats**: Define patterns for proprietary log formats
- **Field Extraction**: Automatically create searchable fields from unstructured text

#### Use Case in This Project

Our Apache logs look like this (unstructured):
```
63.173.168.120 - - [04/Nov/2021:15:07:25 -0500] "GET /search/tag/list HTTP/1.0" 200 5003
```

The Grok processor using `%{COMMONAPACHELOG}` pattern transforms it into structured fields:
```json
{
  "clientip": "63.173.168.120",
  "ident": "-",
  "auth": "-",
  "timestamp": "04/Nov/2021:15:07:25 -0500",
  "verb": "GET",
  "request": "/search/tag/list",
  "httpversion": "1.0",
  "response": "200",
  "bytes": "5003"
}
```

These structured fields can now be searched, filtered, and aggregated in OpenSearch!

---

## Architecture Decision Guide

| Scenario | Use Fluent Bit? | Use Data Prepper? | Use Grok? |
|----------|-----------------|-------------------|-----------|
| Simple log file forwarding to OpenSearch | ✅ Yes | Optional* | No |
| Parse unstructured logs to structured fields | ✅ Yes | ✅ Yes | ✅ Yes |
| High-volume production log ingestion | ✅ Yes | ✅ Yes | ✅ Yes |
| Logs from IoT/Edge devices | ✅ Yes (preferred) | Optional | Depends |
| Complex multi-step processing pipelines | ✅ Yes | ✅ Yes (best for this) | Depends |
| OpenSearch observability with traces/metrics | ❌ No | ✅ Yes | No |
| Lightweight agent-only deployment | ✅ Yes | ❌ No | No |

*Data Prepper is optional if you don't need field parsing and can index raw logs directly.

---

## List of Components

- An OpenSearch domain running through Docker.
- A FluentBit agent running through Docker using `fluent-bit.conf`.
- Data Prepper, which includes a `log_pipeline.yaml` and `data-prepper-config.yaml`for data-prepper server configuration running through Docker.
- An Apache Log Generator in the form of a python script.

### FluentBit And OpenSearch Setup

1. Take a look at the [docker-compose.yaml](docker-compose.yaml). This `docker-compose.yaml` will pull the FluentBit and OpenSearch Docker images and run them in the `log-ingestion_opensearch-net` Docker network.


2. Now take a look at the [fluent-bit.conf](fluent-bit.conf). This config will tell FluentBit to tail the `/var/log/test.log` file for logs, and uses the FluentBit http output plugin to forward these logs to the http source of Data Prepper, which runs by default on port 2021. The `fluent-bit.conf` file
is mounted as a Docker volume through the `docker-compose.yaml`.


3. An empty file named `test.log` has been created. This file is also mounted through the  `docker-compose.yaml`, and will be the file FluentBit is tailing to collect logs from.
   

4. Now that you understand a bit more about how FluentBit and OpenSearch are set up, run them with:

```
docker compose --project-name data-prepper up
```
This we can verify using http://127.0.0.1:5601/

Once we are able to access our opensearch-dashboard we can run data-prepper. 

### Data Prepper Setup
 
1. Take a look at [log_pipeline.yaml](log_pipeline.yaml). This configuration will take logs sent to the [http source](../../data-prepper-plugins/http-source), 
process them with the [Grok Processor](../../data-prepper-plugins/grok-prepper) by matching against the `COMMONAPACHELOG` pattern, 
and send the processed logs to a local [OpenSearch sink](../../data-prepper-plugins/opensearch) to an index named `apache_logs`.

2. And [data-prepper-config.yaml](data-prepper-config.yaml) is also mounted in [docker-compose-dataprepper.yaml](docker-compose-dataprepper.yaml) which will help us to configure our data-prepper server. 


3. Run the Data Prepper docker compose file where we are using `log_pipeline.yaml`. Now FluentBit is able to send logs to the http source of Data Prepper.

Run the following to start Data Prepper:

```
docker compose -f docker-compose-dataprepper.yaml up
```

If Data Prepper is running correctly, you should see something similar to the following line as the latest output in your terminal.

```
INFO org.opensearch.dataprepper.plugins.sink.opensearch.OpenSearchSink - Initialized OpenSearch sink  
INFO org.opensearch.dataprepper.pipeline.Pipeline - Pipeline [log-pipeline] Sink is ready, starting source...  


INFO org.opensearch.dataprepper.plugins.source.loghttp.HTTPSource - Started http source on port 2021...  
INFO org.opensearch.dataprepper.pipeline.Pipeline - Pipeline [log-pipeline] - Submitting request to initiate the pipeline processing
```

### Apache Log Generator

Note that if you just want to see the log ingestion workflow in action, you can simply copy and paste some logs into the `test.log` file yourself without using the Python [Fake Apache Log Generator](https://github.com/graytaylor0/Fake-Apache-Log-Generator). 
Here is a sample batch of randomly generated Apache Logs if you choose to take this route.

```
63.173.168.120 - - [04/Nov/2021:15:07:25 -0500] "GET /search/tag/list HTTP/1.0" 200 5003
71.52.186.114 - - [04/Nov/2021:15:07:27 -0500] "GET /search/tag/list HTTP/1.0" 200 5015
223.195.133.151 - - [04/Nov/2021:15:07:29 -0500] "GET /posts/posts/explore HTTP/1.0" 200 5049
249.189.38.1 - - [04/Nov/2021:15:07:31 -0500] "GET /app/main/posts HTTP/1.0" 200 5005
36.155.45.2 - - [04/Nov/2021:15:07:33 -0500] "GET /search/tag/list HTTP/1.0" 200 5001
4.54.90.166 - - [04/Nov/2021:15:07:35 -0500] "DELETE /wp-content HTTP/1.0" 200 4965
214.246.93.195 - - [04/Nov/2021:15:07:37 -0500] "GET /apps/cart.jsp?appID=4401 HTTP/1.0" 200 5008
72.108.181.108 - - [04/Nov/2021:15:07:39 -0500] "GET /wp-content HTTP/1.0" 200 5020
194.43.128.202 - - [04/Nov/2021:15:07:41 -0500] "GET /app/main/posts HTTP/1.0" 404 4943
14.169.135.206 - - [04/Nov/2021:15:07:43 -0500] "DELETE /wp-content HTTP/1.0" 200 4985
208.0.179.237 - - [04/Nov/2021:15:07:45 -0500] "GET /explore HTTP/1.0" 200 4953
134.29.61.53 - - [04/Nov/2021:15:07:47 -0500] "GET /explore HTTP/1.0" 200 4937
213.229.161.38 - - [04/Nov/2021:15:07:49 -0500] "PUT /posts/posts/explore HTTP/1.0" 200 5092
82.41.77.121 - - [04/Nov/2021:15:07:51 -0500] "GET /app/main/posts HTTP/1.0" 200 5016
```