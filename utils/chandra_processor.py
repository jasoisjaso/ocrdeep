import os
import re
import torch
from transformers import pipeline
from PIL import Image
import logging

from utils.config import OCR_MODEL_NAME, OCR_BATCH_SIZE, PIN_PREFIX_MAPPING, FORM_TYPES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChandraOCR:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        try:
            self.processor = pipeline(
                "image-to-text",
                model=OCR_MODEL_NAME,
                device=self.device,
                batch_size=OCR_BATCH_SIZE,
                # torch_dtype=torch.float16 if self.device == "cuda" else torch.float32 # Enable for faster inference on GPU
            )
            logger.info(f"Successfully loaded OCR model: {OCR_MODEL_NAME}")
        except Exception as e:
            logger.error(f"Error loading OCR model: {e}")
            self.processor = None

    def process_image(self, image_path):
        """
        Processes a single image using the loaded OCR model.
        Returns the extracted text.
        """
        if not self.processor:
            logger.error("OCR model not loaded. Cannot process image.")
            return None
        try:
            image = Image.open(image_path).convert("RGB")
            # The pipeline expects a list of images for batch processing, even for a single image
            result = self.processor(image)
            if result and len(result) > 0:
                return result[0]["generated_text"]
            return None
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return None

    def extract_deduction_data(self, text):
        """
        Extracts structured data from deduction form text.
        """
        data = {
            "name": None,
            "pin": None,
            "date": None,
            "form_type": None,
            "company": "Unknown",
            "errors": []
        }

        # Extract Name (simple heuristic: often near "Name:" or "Employee Name:")
        name_match = re.search(r"(?:Name|Employee Name)[:\s]*([A-Za-z\s.]+)", text, re.IGNORECASE)
        if name_match:
            data["name"] = name_match.group(1).strip()
        else:
            data["errors"].append("Name not found")

        # Extract PIN/Scan Number
        pin_match = re.search(r"(?:PIN|Scan Number|Employee ID)[:\s]*(\d+)", text, re.IGNORECASE)
        if pin_match:
            data["pin"] = pin_match.group(1).strip()
            # Classify company based on PIN prefix
            if data["pin"]:
                prefix = data["pin"][0]
                data["company"] = PIN_PREFIX_MAPPING.get(prefix, "Unknown")
        else:
            data["errors"].append("PIN/Scan Number not found")

        # Extract Date (various formats)
        date_match = re.search(r"(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})", text)
        if date_match:
            data["date"] = date_match.group(1).strip()
        else:
            data["errors"].append("Date not found")

        # Detect Form Type (simple keyword matching)
        detected_form_types = [ft for ft in FORM_TYPES if ft.replace('_', ' ') in text.lower()]
        if detected_form_types:
            # Prioritize specific matches, or just take the first one
            data["form_type"] = detected_form_types[0]
        else:
            data["errors"].append("Form type not detected")

        return data

    def extract_invoice_data(self, text):
        """
        Extracts structured data and line items from invoice text.
        """
        data = {
            "invoice_number": None,
            "date": None,
            "vendor": None,
            "total": None,
            "due_date": None,
            "payment_terms": None,
            "line_items": [],
            "errors": []
        }

        # Extract header data using regex from config
        from utils.config import INVOICE_KEYWORDS
        for key, pattern in INVOICE_KEYWORDS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # For patterns with capturing groups, take the last group as the value
                data[key] = match.group(match.lastindex).strip()
            else:
                data["errors"].append(f"{key.replace('_', ' ').title()} not found")

        # Extract line items (this is a more complex heuristic and might need refinement)
        # Look for patterns like "Qty Description UnitPrice Total"
        line_item_pattern = re.compile(r"(\d+)\s+([A-Za-z0-9\s\-\/]+?)\s+[$€£]?(\d[\d,.]*)\s+[$€£]?(\d[\d,.]*)")
        for line in text.split('\n'):
            item_match = line_item_pattern.search(line)
            if item_match:
                try:
                    qty = int(item_match.group(1))
                    description = item_match.group(2).strip()
                    unit_price = float(item_match.group(3).replace(',', ''))
                    item_total = float(item_match.group(4).replace(',', ''))
                    data["line_items"].append({
                        "qty": qty,
                        "description": description,
                        "unit_price": unit_price,
                        "total": item_total
                    })
                except ValueError:
                    data["errors"].append(f"Could not parse line item: {line}")
        if not data["line_items"]:
            data["errors"].append("No line items detected")

        return data

# Example usage (for testing purposes)
if __name__ == "__main__":
    # Create a dummy image for testing
    from PIL import Image, ImageDraw, ImageFont
    dummy_image_path = "dummy_invoice.png"
    img = Image.new('RGB', (800, 600), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        # Try to use a common font, or default if not found
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()

    d.text((50,50), "Invoice # INV-2023-001", fill=(0,0,0), font=font)
    d.text((50,90), "Date: 10/11/2025", fill=(0,0,0), font=font)
    d.text((50,130), "Vendor: Example Corp", fill=(0,0,0), font=font)
    d.text((50,170), "Total: $123.45", fill=(0,0,0), font=font)
    d.text((50,210), "Due Date: 25/11/2025", fill=(0,0,0), font=font)
    d.text((50,250), "Payment Terms: Net 30", fill=(0,0,0), font=font)
    d.text((50,300), "Qty Description Unit Price Total", fill=(0,0,0), font=font)
    d.text((50,340), "1   Item A      100.00      100.00", fill=(0,0,0), font=font)
    d.text((50,370), "2   Item B      11.72       23.44", fill=(0,0,0), font=font)
    img.save(dummy_image_path)

    ocr_processor = ChandraOCR()
    if ocr_processor.processor:
        print(f"\n--- Processing {dummy_image_path} ---")
        extracted_text = ocr_processor.process_image(dummy_image_path)
        if extracted_text:
            print("\nExtracted Text:\n", extracted_text)
            invoice_data = ocr_processor.extract_invoice_data(extracted_text)
            print("\nExtracted Invoice Data:\n", invoice_data)
        else:
            print("Failed to extract text.")
    else:
        print("OCR processor not initialized.")

    # Clean up dummy image
    if os.path.exists(dummy_image_path):
        os.remove(dummy_image_path)

    # Test deduction form data extraction
    deduction_text = """
    Employee Name: John Doe
    PIN: 212345
    Date: 01/01/2025
    Form Type: Uniforms Request
    """
    print("\n--- Testing Deduction Form Extraction ---")
    deduction_data = ocr_processor.extract_deduction_data(deduction_text)
    print("\nExtracted Deduction Data:\n", deduction_data)

    deduction_text_adecco = """
    Employee Name: Jane Smith
    Scan Number: 67890
    Date: 02-02-2025
    Form Type: Access Cards Application
    """
    print("\n--- Testing Adecco Deduction Form Extraction ---")
    deduction_data_adecco = ocr_processor.extract_deduction_data(deduction_text_adecco)
    print("\nExtracted Deduction Data:\n", deduction_data_adecco)
