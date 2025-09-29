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
