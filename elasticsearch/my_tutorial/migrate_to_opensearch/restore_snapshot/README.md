# Gotchas
- The docker images `curlimages/curl` or `alpine/curl` (which are the tiniest < 10mb) are throwing error on unrecognized option P on `grep -oP` in the restoration script, hence switched to using ubuntu/curl
- For opensearch restore, disable security (see environment in docker compose)