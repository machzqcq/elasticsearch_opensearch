# STEMMING

# Stemming is the process of reducing a word to its root form. This ensures variants of a word match during a search.

# For example, walking and walked can be stemmed to the same root word: walk. Once stemmed, an occurrence of either word would match the other in a search.

# Stemming is language-dependent but often involves removing prefixes and suffixes from words.

# In some cases, the root form of a stemmed word may not be a real word. For example, jumping and jumpiness can both be stemmed to jumpi. While jumpi isn’t a real English word, it doesn’t matter for search; if all variants of a word are reduced to the same root form, they will match correctly


# ANALYZER
# An analyzer  — whether built-in or custom — is just a package which contains three lower-level building blocks: character filters, tokenizers, and token filters.
# Test an analyzer

POST _analyze
{
  "analyzer": "whitespace",
  "text":     "The quick brown fox."
}

POST _analyze
{
  "tokenizer": "standard",
  "filter":  [ "lowercase", "asciifolding" ],
  "text":      "Is this déja vu?"
}

# A custom analyzer
PUT my-index-000001
{
  "settings": {
    "analysis": {
      "analyzer": {
        "std_folded": { 
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "asciifolding"
          ]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "my_text": {
        "type": "text",
        "analyzer": "std_folded" 
      }
    }
  }
}

GET my-index-000001/_analyze 
{
  "analyzer": "std_folded", 
  "text":     "Is this déjà vu?"
}

GET my-index-000001/_analyze 
{
  "field": "my_text", 
  "text":  "Is this déjà vu?"
}

# CONFIGURING BUILT-IN ANALYZERS
PUT my-index-000001
{
  "settings": {
    "analysis": {
      "analyzer": {
        "std_english": { 
          "type":      "standard",
          "stopwords": "_english_"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "my_text": {
        "type":     "text",
        "analyzer": "standard", 
        "fields": {
          "english": {
            "type":     "text",
            "analyzer": "std_english" 
          }
        }
      }
    }
  }
}

POST my-index-000001/_analyze
{
  "field": "my_text", 
  "text": "The old brown cow"
}

POST my-index-000001/_analyze
{
  "field": "my_text.english", 
  "text": "The old brown cow"
}

# CREATING CUSTOM ANALYZERS
# https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-custom-analyzer.html
# When the built-in analyzers do not fulfill your needs, you can create a custom analyzer which uses the appropriate combination of:

#     zero or more character filters
#     a tokenizer
#     zero or more token filters.

# Example configuration

# Here is an example that combines the following:

# Character Filter

#         HTML Strip Character Filter

# Tokenizer

#         Standard Tokenizer

# Token Filters

#         Lowercase Token Filter
#         ASCII-Folding Token Filter

PUT my-index-000001
{
  "settings": {
    "analysis": {
      "analyzer": {
        "my_custom_analyzer": {
          "type": "custom", 
          "tokenizer": "standard",
          "char_filter": [
            "html_strip"
          ],
          "filter": [
            "lowercase",
            "asciifolding"
          ]
        }
      }
    }
  }
}

POST my-index-000001/_analyze
{
  "analyzer": "my_custom_analyzer",
  "text": "Is this <b>déjà vu</b>?"
}

# SPECIFY ANALYZER AT SEARCH TIME/QUERY TIME
GET my-index-000001/_search
{
  "query": {
    "match": {
      "message": {
        "query": "Quick foxes",
        "analyzer": "stop"
      }
    }
  }
}

# Specify search analyzer for a field

PUT my-index-000001
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "whitespace",
        "search_analyzer": "simple"
      }
    }
  }
}

# LANGUAGE ANALYZERS
# https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-lang-analyzer.html
# stopwords, exluding words from stemming, etc.