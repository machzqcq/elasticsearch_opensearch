# DeepSeek Integration Guide

## 📚 Overview
Integration of **DeepSeek** models with OpenSearch for cost-effective LLM capabilities with strong code understanding.

### 🎯 Supported Models
- `deepseek-chat` - General purpose, conversational
- `deepseek-coder` - Code generation and analysis

---

## 🔄 Quick Setup

```python
# Create connector
connector_body = {
    "name": "DeepSeek Connector",
    "protocol": "http",
    "parameters": {
        "endpoint": "api.deepseek.com",
        "model": "deepseek-chat"
    },
    "credential": {
        "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY")
    }
}
```

---

## ✨ Key Advantages

- ✅ **Cost-effective** pricing
- ✅ **Open weights** - can self-host
- ✅ **Strong code** understanding
- ✅ **Good reasoning** abilities

---

## 💰 Pricing

```
DeepSeek is significantly cheaper than OpenAI/Anthropic
~10x lower cost than GPT-4
```

---

## 🎯 Best For

- 💻 **Code generation**
- 💰 **Budget-conscious** projects
- 🔄 **Technical content** generation

---

## 📖 Resources

- 🔗 [DeepSeek API](https://www.deepseek.com/api)

