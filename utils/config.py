import os

# Base directory for temporary files
TEMP_DIR = os.path.join(os.getcwd(), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# OCR Model Configuration
# Using a powerful Hugging Face model for document understanding
OCR_MODEL_NAME = "facebook/nougat-base" 
# You might need to adjust this based on your GPU memory
# For RTX 4060 Ti (16GB VRAM), a batch size of 1-2 might be appropriate for nougat-base
OCR_BATCH_SIZE = 1 

# Paths for output
OUTPUT_DIR = os.path.join(os.getcwd(), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Deduction Form Classification
PIN_PREFIX_MAPPING = {
    "2": "Primary Connect",
    "5": "Chandler",
    "6": "Adecco",
}
FORM_TYPES = ["uniforms", "access_cards", "headsets"]

# Invoice Extraction Keywords (example, will need refinement)
INVOICE_KEYWORDS = {
    "invoice_number": r"(invoice|bill|receipt)\\s*#?\\\s*(\\w+)",
    "date": r"(\\d{1,2}[-/.]\\d{1,2}[-/.]\\d{2,4})",
    "vendor": r"(?:from|by)\\s*([A-Za-z0-9\\s,. ]+)\\s*(?:\\n|invoice)",
    "total": r"(total|balance due)\\s*[$€£]?\\s*(\\d[\\d,.]*)",
    "due_date": r"(due date|payment due)\\s*[:]?\\s*(\\d{1,2}[-/.]\\d{1,2}[-/.]\\d{2,4})",
    "payment_terms": r"(payment terms|terms)\\s*[:]?\\s*([A-Za-z0-9\\s,. ]+)",
}

# Streamlit Theme
DEFAULT_THEME = "dark" # or "light"
