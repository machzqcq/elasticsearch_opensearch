# Restore Gotchas
- Opensearch is very strict on restore index (requires ssl and admin certs etc) - https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/#security-considerations
- Check the flag IS_AUTH at the top of python code