PUT _cluster/settings
{
  "persistent": {
    "plugins": {
      "ml_commons": {
        "allow_registering_model_via_url": "true",
        "only_run_on_ml_node": "false",
        "model_access_control_enabled": "true",
        "native_memory_threshold": "99"
      }
    }
  }
}

POST /_plugins/_ml/model_groups/_register
{
  "name": "local_model_group",
  "description": "A model group for local models"
}


POST /_plugins/_ml/models/_register
{
  "name": "huggingface/sentence-transformers/msmarco-distilbert-base-tas-b",
  "version": "1.0.1",
  "model_group_id": "EteBjZkBgo2rRKNSkrCa",
  "description": "This is a port of the DistilBert TAS-B Model to sentence-transformers model: It maps sentences and paragraphs to a 768 dimensional dense vector space and is optimized for the task of semantic search.",
  "function_name": "TEXT_EMBEDDING",
  "model_format": "TORCH_SCRIPT",
  "model_content_size_in_bytes": 266352827,
  "model_content_hash_value": "acdc81b652b83121f914c5912ae27c0fca8fabf270e6f191ace6979a19830413",
  "model_config": {
    "model_type": "distilbert",
    "embedding_dimension": 768,
    "framework_type": "sentence_transformers",
    "all_config": """{"_name_or_path":"old_models/msmarco-distilbert-base-tas-b/0_Transformer","activation":"gelu","architectures":["DistilBertModel"],"attention_dropout":0.1,"dim":768,"dropout":0.1,"hidden_dim":3072,"initializer_range":0.02,"max_position_embeddings":512,"model_type":"distilbert","n_heads":12,"n_layers":6,"pad_token_id":0,"qa_dropout":0.1,"seq_classif_dropout":0.2,"sinusoidal_pos_embds":false,"tie_weights_":true,"transformers_version":"4.7.0","vocab_size":30522}"""
  },
  "created_time": 1676073973126,
  "url": "https://artifacts.opensearch.org/models/ml-models/huggingface/sentence-transformers/msmarco-distilbert-base-tas-b/1.0.1/torch_script/sentence-transformers_msmarco-distilbert-base-tas-b-1.0.1-torch_script.zip"
}

GET /_plugins/_ml/tasks/FteCjZkBgo2rRKNSd7B1

POST /_plugins/_ml/models/GteCjZkBgo2rRKNSebAQ/_deploy

GET /_plugins/_ml/tasks/KteDjZkBgo2rRKNSNbCL

POST /_plugins/_ml/_predict/text_embedding/GteCjZkBgo2rRKNSebAQ
{
  "text_docs":[ "today is sunny"],
  "return_number": true,
  "target_response": ["sentence_embedding"]
}
