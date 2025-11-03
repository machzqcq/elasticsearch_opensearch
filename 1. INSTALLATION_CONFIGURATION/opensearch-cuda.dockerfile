# Start with OpenSearch 3.2.0 as the base image
FROM opensearchproject/opensearch:3.3.0

USER root
# Install required packages
RUN dnf install -y \
    sudo \
    wget \
    which \
    gcc \
    make \
    dkms

# Add NVIDIA CUDA repository
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo -O /etc/yum.repos.d/cuda-rhel9.repo

# Install CUDA toolkit and libraries
RUN dnf clean all && \
    dnf -y module install nvidia-driver:latest-dkms && \
    dnf -y install cuda && \
    dnf -y install cuda-toolkit
    

USER opensearch
# Set environment variables
ENV PATH=/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

# Verify CUDA installation
RUN nvidia-smi

# Start OpenSearch
CMD ["opensearch"]