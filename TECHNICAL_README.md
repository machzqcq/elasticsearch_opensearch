# Installation
- `sudo swapoff -a` - I did not do this as Increased risk of system crashes: Without a pagefile, when physical RAM runs out, the system or software will instantly crash instead of slowing down as it would with paging enabled
- `sysctl vm.max_map_count` - default 65530, Increase temporarily in the shell `sudo sysctl -w vm.max_map_count=262144`, permanently add to `/etc/sysctl.conf
- `curl -H "Content-Type: application/x-ndjson" -X PUT "https://localhost:9200/ecommerce" -ku admin:<custom-admin-password> --data-binary "@ecommerce-field_mappings.json"`
- `curl -H "Content-Type: application/x-ndjson" -X PUT "https://localhost:9200/ecommerce/_bulk" -ku admin:<custom-admin-password> --data-binary "@ecommerce.json"`

# Python
- System python = 3.12.11
- Using (uv)[https://github.com/astral-sh/uv] as python package manager (various reasons - read online. The biggest benefit for me was speed)
- Install uv - `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `cd opensearch` and run the command `uv sync` - Will create a .venv directory that contains your python client environment 
- `source .venv/bin/activate` - to activate the current shell with python 3.12.11

# Java
- OpenJDK 21 or higher
- Ubuntu install `sudo apt install openjdk-21-jdk`
- Check java version `java -version`

# Load interns parquet
- `source .venv/bin/activate` - if not done already
- `export OPENSEARCH_INITIAL_ADMIN_PASSWORD=Developer@123`
- `docker compose -f docker-compose-opensearch-single-2.16.0.yml up -d`
- `docker compose -f docker-compose-opensearch-single-2.16.0.yml logs -f` to check if all is well
- `docker compose -f docker-compose-opensearch-single-2.16.0.yml down` - to stop and remove all
- `python3 interns_sample_load.py`