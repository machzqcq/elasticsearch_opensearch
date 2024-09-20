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

# Gotchas
- With 2.16.0, though OPENSEARCH_INITIAL_ADMIN_PASSWORD is not required, if we mention that in enviroment, it needs to have a value in shell, otherwise services don't start properly