from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

# Load the model and tokenizer
model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name, return_dict=False)

# Set the model to evaluation mode
model.eval()

# Create a sample input for tracing
question = "What is the capital of France?"
context = "Paris is the capital and most populous city of France."
inputs = tokenizer(question, context, return_tensors="pt")

# Trace the model
traced_model = torch.jit.trace(model, (inputs['input_ids'], inputs['attention_mask']))

# Save the traced model
torch.save(traced_model.state_dict(), "question_answering_pt.pt")

# Save the tokenizer
tokenizer.save_pretrained("tokenizer")

# Save the model configuration
model.config.save_pretrained("model_config")