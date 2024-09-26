# While running python3 sample_ingest.py
## Context
- 2.17.0 with master (aka. opensearch-node1) has JAVA_OPTS=4096 for both min and max (master needs to have high heap)
- CLUSTER ISSUES: cluster starts up fine, but kNN index creation and circuit breaker conditions in the cluster cause errors
![alt text](image.png)
- Further opensearchknn lib needs to be added to LD_LIBRARY_PATH (see docker compose)
- https://github.com/opensearch-project/ml-commons/issues/2838 (the fix was to change the engine to lucene from the other values `nmslib`)
- Ultimately to make sample_ingest.py run without fail (i.e. create model ....index creation..sample data upload), we need big machines (as LLMs require that for embeddings). So best to create it manually through kibana dev tools until opensearch-ml python library matures a bit more
- The reasons are mentioned in CIRCUIT BREAKER exceptions for opensearch and there are many settings that master node ensure are in place (read online with circuit breaker exceptions)
- SINGLE NODE: This works fine without issues (for kNN index with `docker-compose-opensearch-single-2.16.0.yml`)