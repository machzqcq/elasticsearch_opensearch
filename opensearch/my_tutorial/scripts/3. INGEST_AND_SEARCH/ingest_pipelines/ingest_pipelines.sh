PUT _ingest/pipeline/my-pipeline
{
  "description": "This pipeline processes student data",
  "processors": [
    {
      "set": {
        "description": "Sets the graduation year to 2023",
        "field": "grad_year",
        "value": 2023
      }
    },
    {
      "set": {
        "description": "Sets graduated to true",
        "field": "graduated",
        "value": true
      }
    },
    {
      "uppercase": {
        "field": "name"
      }
    }
  ]
}

GET _ingest/pipeline/
GET _ingest/pipeline/my-pipeline
DELETE /_ingest/pipeline/my-pipeline

POST /_ingest/pipeline/my-pipeline/_simulate
{
  "docs": [
    {
      "_index": "my-index",
      "_id": "1",
      "_source": {
        "grad_year": 2024,
        "graduated": "",
        "name": "John Doe"
      }
    },
    {
      "_index": "my-index",
      "_id": "2",
      "_source": {
        "grad_year": 2025,
        "graduated": false,
        "name": "Jane Doe"
      }
    }
  ]
}


# Specify a pipeline in the request body - without creating it first
POST /_ingest/pipeline/_simulate
{
  "pipeline" :
  {
    "description": "Splits text on white space characters",
    "processors": [
      {
        "csv" : {
          "field" : "name",
          "separator": ",",
          "target_fields": ["last_name", "first_name"],
          "trim": true
        }
      },
      {
      "uppercase": {
        "field": "last_name"
      }
    }
    ]
  },
  "docs": [
    {
      "_index": "second-index",
      "_id": "1",
      "_source": {
        "name": "Doe,John"
      }
    },
    {
      "_index": "second-index",
      "_id": "2",
      "_source": {
        "name": "Doe, Jane"
      }
    }
  ]
}

# Access input data in a pipeline - using ctx object
PUT _ingest/pipeline/example-pipeline
{
  "description": "Sets tags, log label, and defaults error message",
  "processors": [
    {
      "set": {
        "field": "tagline",
        "value": "{{{user.first}}} from {{{department}}}"
      }
    },
    {
      "script": {
        "lang": "painless",
        "source": "ctx.year = ctx.date.substring(0, 4);"
      }
    },
    {
      "set": {
        "field": "received_at",
        "value": "{{_ingest.timestamp}}"
      }
    }
  ]
}

POST _ingest/pipeline/example-pipeline/_simulate
{
  "docs": [
    {
      "_source": {
        "user": {
          "first": "Liam"
        },
        "department": "Engineering",
        "date": "2024-12-03T14:05:00Z"
      }
    }
  ]
}

# Conditional 
# The following pipeline drops any document in which the log_level field is equal to debug
PUT _ingest/pipeline/drop_debug_logs
{
  "processors": [
    {
      "drop": {
        "if": "ctx.log_level == 'debug'"
      }
    }
  ]
}

POST logs/_doc/1?pipeline=drop_debug_logs
{
  "message": "User logged in",
  "log_level": "debug"
}

POST logs/_doc/1?pipeline=drop_debug_logs
{
  "message": "User logged in",
  "log_level": "info"
}

# Multi-step conditional pipeline
# The following ingest pipeline uses three processors:
# set: If no value is provided in the user field, sets the user field to guest.
# set: If the status_code is provided and is higher than 400, sets the error field to true.
# drop: If the app.env field exists & is equal to debug, drops the entire document.

PUT _ingest/pipeline/logs_processing
{
  "processors": [
    {
      "set": {
        "field": "user",
        "value": "guest",
        "if": "ctx.user == null"
      }
    },
    {
      "set": {
        "field": "error",
        "value": true,
        "if": "ctx.status_code != null && ctx.status_code >= 400"
      }
    },
    {
      "drop": {
        "if": "ctx.app?.env == 'debug'"
      }
    }
  ]
}

POST _ingest/pipeline/logs_processing/_simulate
{
  "docs": [
    {
      "_source": {
        "message": "Successful login",
        "status_code": 200
      }
    },
    {
      "_source": {
        "message": "Database error",
        "status_code": 500,
        "user": "alice"
      }
    },
    {
      "_source": {
        "message": "Debug mode trace",
        "app": { "env": "debug" }
      }
    }
  ]
}

# pipeline processor
# The following example demonstrates how to route logs to different sub-pipelines depending on the service.name field in the document

PUT _ingest/pipeline/webapp_logs
{
  "processors": [
    { "set": { "field": "log_type", "value": "webapp" } }
  ]
}

PUT _ingest/pipeline/api_logs
{
  "processors": [
    { "set": { "field": "log_type", "value": "api" } }
  ]
}

PUT _ingest/pipeline/service_router
{
  "processors": [
    {
      "pipeline": {
        "name": "webapp_logs",
        "if": "ctx.service?.name == 'webapp'"
      }
    },
    {
      "pipeline": {
        "name": "api_logs",
        "if": "ctx.service?.name == 'api'"
      }
    }
  ]
}

POST _ingest/pipeline/service_router/_simulate
{
  "docs": [
    { "_source": { "service": { "name": "webapp" }, "message": "Homepage loaded" } },
    { "_source": { "service": { "name": "api" }, "message": "GET /v1/users" } },
    { "_source": { "service": { "name": "worker" }, "message": "Task started" } }
  ]
}

# Regex conditionals
# Email domain filtering

PUT _ingest/pipeline/tag_example_com_users
{
  "processors": [
    {
      "set": {
        "field": "user_domain",
        "value": "example.com",
        "if": "ctx.email != null && ctx.email =~ /@example.com$/"
      }
    }
  ]
}

POST _ingest/pipeline/tag_example_com_users/_simulate
{
  "docs": [
    { "_source": { "email": "alice@example.com" } },
    { "_source": { "email": "bob@another.com" } }
  ]
}

# Detect IPv6 addresses
PUT _ingest/pipeline/ipv6_flagger
{
  "processors": [
    {
      "set": {
        "field": "ip_type",
        "value": "IPv6",
        "if": "ctx.ip != null && ctx.ip =~ /^[a-fA-F0-9:]+$/ && ctx.ip.contains(':')"
      }
    }
  ]
}

POST _ingest/pipeline/ipv6_flagger/_simulate
{
  "docs": [
    { "_source": { "ip": "2001:0db8:85a3:0000:0000:8a2e:0370:7334" } },
    { "_source": { "ip": "192.168.0.1" } }
  ]
}

# Validate UUID strings
PUT _ingest/pipeline/uuid_checker
{
  "processors": [
    {
      "set": {
        "field": "valid_uuid",
        "value": true,
        "if": "ctx.session_id != null && ctx.session_id =~ /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/"
      }
    }
  ]
}

POST _ingest/pipeline/uuid_checker/_simulate
{
  "docs": [
    { "_source": { "session_id": "550e8400-e29b-41d4-a716-446655440000" } },
    { "_source": { "session_id": "invalid-uuid-1234" } }
  ]
}


