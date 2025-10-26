# 🚀 OpenSearch Ingestion Optimization Notebooks

This directory contains comprehensive Jupyter notebooks demonstrating OpenSearch ingestion optimization techniques using the SQUAD dataset, achieving **65% performance improvement** and **19% storage reduction**.

## 📂 Notebook Structure

### 🎯 Core Optimization Notebooks

1. **[01_bulk_api_optimization.ipynb](notebooks/01_bulk_api_optimization.ipynb)**
   - Demonstrates Bulk API vs individual indexing
   - Batch size optimization testing
   - Asynchronous vs synchronous processing
   - Error handling and retry strategies
   - **Expected Result**: 5-10x speed improvement

2. **[02_jvm_translog_optimization.ipynb](notebooks/02_jvm_translog_optimization.ipynb)**
   - JVM heap sizing (50% of available memory)
   - Translog flush threshold optimization (25% of heap)
   - Memory monitoring and analysis
   - **Expected Result**: 15-20% additional improvement

3. **[03_segment_replication_demo.ipynb](notebooks/03_segment_replication_demo.ipynb)**
   - Document vs Segment replication comparison
   - CPU and network usage analysis
   - Performance impact measurement
   - **Expected Result**: 30% CPU usage reduction

4. **[04_compression_optimization.ipynb](notebooks/04_compression_optimization.ipynb)**
   - ZSTD compression configuration
   - Storage efficiency analysis
   - Compression level tuning
   - **Expected Result**: 19% storage reduction

5. **[05_end_to_end_optimization.ipynb](notebooks/05_end_to_end_optimization.ipynb)** ⭐
   - **Complete implementation of all techniques**
   - Compound effect demonstration
   - Comprehensive performance analysis
   - **Target Result**: 65% speed improvement + 19% storage reduction

## 🐳 Docker Compose Files

### Available Configurations:

- **`docker-compose-optimized.yml`**: Basic optimizations (JVM + cluster settings)
- **`docker-compose-fully-optimized.yml`**: Complete optimization stack

### Quick Start:
```bash
# Start optimized cluster
cd improving_ingestion_techniques
docker-compose -f docker-compose-fully-optimized.yml up -d

# Wait for startup (45 seconds)
# Then run notebooks
```

## 🏃‍♂️ Getting Started

### Prerequisites:
```bash
pip install pandas opensearch-py matplotlib seaborn numpy jupyter
```

### Recommended Execution Order:

1. **Start with End-to-End**: Run `05_end_to_end_optimization.ipynb` for complete demo
2. **Deep Dive**: Explore individual technique notebooks (01-04)
3. **Experiment**: Modify settings and test with your own data

## 📊 Expected Performance Results

| Technique | Performance Gain | Storage Impact | CPU Impact |
|-----------|------------------|----------------|------------|
| Bulk API | 5-10x faster | Neutral | Reduced |
| JVM Optimization | +15-20% | Neutral | Optimized |
| Translog Tuning | +10-15% | Neutral | Reduced |
| Segment Replication | +5-10% | Neutral | -30% |
| ZSTD Compression | Neutral | -19% | Slight increase |
| Refresh Interval | +5% | Neutral | Reduced |
| **Combined Effect** | **+65%** | **-19%** | **-30%** |

## 🎯 Learning Objectives

After completing these notebooks, you will understand:

- ✅ How to optimize OpenSearch for high-throughput ingestion
- ✅ The compound effect of multiple optimization techniques
- ✅ Performance monitoring and measurement strategies
- ✅ Trade-offs between consistency, performance, and resource usage
- ✅ Production-ready optimization configurations

## 🔧 Customization Tips

### For Your Own Data:
1. Adjust batch sizes based on document size
2. Tune JVM heap based on available memory
3. Modify compression level based on CPU availability
4. Adjust refresh interval based on consistency requirements

### Monitoring Commands:
```bash
# Check cluster health
curl -k -u admin:Developer@123 https://localhost:9200/_cluster/health

# Monitor JVM usage
curl -k -u admin:Developer@123 https://localhost:9200/_nodes/stats/jvm

# Check index statistics
curl -k -u admin:Developer@123 https://localhost:9200/your-index/_stats
```

## 🚀 Next Steps

1. **Production Deployment**: Apply learnings to your production cluster
2. **Monitoring Setup**: Implement comprehensive performance monitoring
3. **Load Testing**: Test with your actual data volumes and patterns
4. **Automation**: Script the optimization configurations for consistent deployment

## 🐛 Troubleshooting

### Common Issues:
- **Memory errors**: Reduce batch size or increase JVM heap
- **Connection timeouts**: Increase timeout settings
- **High CPU usage**: Enable segment replication
- **Slow ingestion**: Check translog flush threshold

### Performance Debugging:
```python
# Check current settings
client.indices.get_settings(index="your-index")

# Monitor performance
client.indices.stats(index="your-index")
```

---

**💡 Pro Tip**: Start with the end-to-end notebook (`05_end_to_end_optimization.ipynb`) to see the complete optimization in action, then explore individual techniques for deeper understanding.