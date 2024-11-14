# Installation
- `sudo swapoff -a` - I did not do this as Increased risk of system crashes: Without a pagefile, when physical RAM runs out, the system or software will instantly crash instead of slowing down as it would with paging enabled
- `sysctl vm.max_map_count` - default 65530, Increas temporarily in the shell `sudo sysctl -w vm.max_map_count=262144`, permanently add to `/etc/sysctl.conf
- `curl -H "Content-Type: application/x-ndjson" -X PUT "https://192.168.0.111:9200/ecommerce" -ku admin:<custom-admin-password> --data-binary "@ecommerce-field_mappings.json"`
- `curl -H "Content-Type: application/x-ndjson" -X PUT "https://192.168.0.111:9200/ecommerce/_bulk" -ku admin:<custom-admin-password> --data-binary "@ecommerce.json"`

# Python
- System python = 3.8.10 and created venv from it
- `source venv/bin/activate` 
- `pip3 install -r requirements.txt`

# Load interns parquet
- `source venv/bin/activate` - if not done already
- `export OPENSEARCH_INITIAL_ADMIN_PASSWORD=Padmasini10`
- `docker compose -f docker-compose-opensearch-single-2.16.0.yml up -d`
- `docker compose -f docker-compose-opensearch-single-2.16.0.yml logs -f` to check if all is well
- `docker compose -f docker-compose-opensearch-single-2.16.0.yml down` - to stop and remove all
- `python3 interns_sample_load.py`

# Ingest script as part of docker compose
~~Though we are able to execute every step in the shell script (setup_ml.sh), as part of docker file, model group ID is not getting generated, so all subsequent steps fail~~

# Gotchas
- With 2.16.0, though OPENSEARCH_INITIAL_ADMIN_PASSWORD is not required, if we mention that in enviroment, it needs to have a value in shell, otherwise services don't start properly

## While running python3 sample_ingest.py
### Context
- 2.17.0 with master (aka. opensearch-node1) has JAVA_OPTS=4096 for both min and max (master needs to have high heap)
- CLUSTER ISSUES: cluster starts up fine, but kNN index creation and circuit breaker conditions in the cluster cause errors
![alt text](image.png)
- Further opensearchknn lib needs to be added to LD_LIBRARY_PATH (see docker compose)
- https://github.com/opensearch-project/ml-commons/issues/2838 (the fix was to change the engine to lucene from the other values `nmslib`)
- Ultimately to make sample_ingest.py run without fail (i.e. create model ....index creation..sample data upload), we need big machines (as LLMs require that for embeddings). So best to create it manually through kibana dev tools until opensearch-ml python library matures a bit more
- The reasons are mentioned in CIRCUIT BREAKER exceptions for opensearch and there are many settings that master node ensure are in place (read online with circuit breaker exceptions)
- SINGLE NODE: This works fine without issues (for kNN index with `docker-compose-opensearch-single-2.16.0.yml`)
- `POSSIBLE FIX (YMMV):` Ensure you have heap at least 4gb and and `engine: lucene` on knn_vector