# Installation
- `sudo swapoff -a` - I did not do this as Increased risk of system crashes: Without a pagefile, when physical RAM runs out, the system or software will instantly crash instead of slowing down as it would with paging enabled
- `sysctl vm.max_map_count` - default 65530, Increas temporarily in the shell `sudo sysctl -w vm.max_map_count=262144`, permanently add to `/etc/sysctl.conf
- `curl -H "Content-Type: application/x-ndjson" -X PUT "https://192.168.0.111:9200/ecommerce" -ku admin:<custom-admin-password> --data-binary "@ecommerce-field_mappings.json"`
- `curl -H "Content-Type: application/x-ndjson" -X PUT "https://192.168.0.111:9200/ecommerce/_bulk" -ku admin:<custom-admin-password> --data-binary "@ecommerce.json"`