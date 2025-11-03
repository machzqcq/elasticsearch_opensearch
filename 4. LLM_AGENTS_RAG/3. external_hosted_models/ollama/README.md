# Gotchas

## Listen on 0.0.0.0


### Linux 
```sh
#!/bin/bash

# Steps to configure Ollama to listen on 0.0.0.0

# 1. Edit the Ollama service configuration
# Open the service override file for Ollama
sudo systemctl edit ollama.service

# In the editor, add the following lines under the [Service] section:
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_ORIGINS=*"
# OLLAMA_HOST=0.0.0.0:11434 configures Ollama to listen on all interfaces on port 11434.
# OLLAMA_ORIGINS=* allows connections from any origin for remote access.

# 2. Save and close the file, then reload the systemd daemon and restart Ollama
sudo systemctl daemon-reload
sudo systemctl restart ollama.service

# 3. (Optional) Verify the service status
sudo systemctl status ollama.service

# 4. (Optional) Verify open ports
sudo ss -tuln | grep 11434
# You should see an entry like 0.0.0.0:11434 if Ollama is listening on all interfaces.
```

## Windows
- Edit your system environment variables (need to be admin)
- Add `OLLAMA_HOST=0.0.0.0:11434` entry
- Restart ollama service

## Gotchas
- `ollama_connector_embedding.py`: We used OLLAMA_IP_URL (ip instead of host) because the client python code runs on host and it doesn't know the DNS name `ollama` which is the docker defined dns for ollama container. Hence we port map ollama port 11434 to host's 11435 and hence opensearch service (running in os container) can also talk to IP. Of course it can talk to dns ollama also. In production workloads, as long as ollama service is reachable on network to OS service - we should be good.
- `ollama_connector_embedding_lite.py`: This script uses `ollama` host value since the process fully runs in docker containers. 
