import torch
from transformers import AutoModelForVision2Seq, AutoTokenizer
from PIL import Image
import yaml
import json
import re

# This script is for testing the OCR model inside the worker container.
# To use it, you need to have a sample image named 'sample_image.png'
# in the same directory as this script.

# Load Model
MODEL_NAME = "deepseek-ai/DeepSeek-OCR"
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModelForVision2Seq.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)
model.eval()

print(f"DeepSeek-OCR model loaded on {device}")

# Load Prompt Config
with open("prompts/absence_form.yaml", "r") as f:
    config = yaml.safe_load(f)

prompt = config['prompt_template']

# Load Image
try:
    image = Image.open("sample_image.png").convert("RGB")
except FileNotFoundError:
    print("Error: sample_image.png not found. Please place a sample image in the worker directory.")
    exit()

# Prepare for model
inputs = tokenizer(image, return_tensors="pt").to(model.device)

# Generate
response = model.generate(
    **inputs,
    max_new_tokens=1024,
    use_cache=True,
    do_sample=False,
)

# Decode and Parse
result_text = tokenizer.decode(response[0], skip_special_tokens=True)
print("---"Model Output"---")
print(result_text)

try:
    json_match = re.search(r"{\n.*\n}", result_text, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON object found in model output")
    
    extracted_data = json.loads(json_match.group(0))
    print("---"Parsed JSON"---")
    print(json.dumps(extracted_data, indent=2))
except (json.JSONDecodeError, ValueError) as e:
    print("---"Error"---")
    print(f"Error parsing JSON from model output: {e}")
