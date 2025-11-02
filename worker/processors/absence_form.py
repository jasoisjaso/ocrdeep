from .base import DocumentProcessor
import yaml
import os
import re
import json

class AbsenceFormProcessor(DocumentProcessor):
    def load_prompt_config(self):
        with open("/app/prompts/absence_form.yaml", "r") as f:
            return yaml.safe_load(f)

from tenacity import retry, stop_after_attempt, wait_fixed
import json

class AbsenceFormProcessor(DocumentProcessor):
    def load_prompt_config(self):
        with open("/app/prompts/absence_form.yaml", "r") as f:
            return yaml.safe_load(f)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def extract_from_image(self, image, model, tokenizer, config):
        prompt = config['prompt_template']
        
        # The DeepSeek-OCR model has a custom run_ocr method
        data = model.run_ocr(image, tokenizer, prompt=prompt, max_new_tokens=1024, use_cache=True, do_sample=False)
        
        # Decode and parse
        result_text = tokenizer.decode(data[0], skip_special_tokens=True)
        
        try:
            # The model should return a JSON string. We need to find it in the output.
            json_match = re.search(r"{\n.*\n}", result_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in model output")
            
            extracted_data = json.loads(json_match.group(0))
            return extracted_data
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing JSON from model output: {e}")
            raise


    def validate_data(self, data):
        config = self.load_prompt_config()
        for field in config.get('required_fields', []):
            if not data.get(field):
                return False
        return True

    def save_page(self, image, data, output_base, page_num):
        config = self.load_prompt_config()
        sorting_field = config['sorting_logic']['field']
        sorting_value = data.get(sorting_field, '')

        target_folder = 'Misc' # Default
        for rule in config['sorting_logic']['rules']:
            if 'pattern' in rule and re.match(rule['pattern'], sorting_value):
                target_folder = rule['folder']
                break
            elif 'default' in rule:
                target_folder = rule['default']

        save_dir = os.path.join(output_base, target_folder)
        os.makedirs(save_dir, exist_ok=True)
        image.save(os.path.join(save_dir, f"page_{page_num}.png"))

        with open(os.path.join(save_dir, f"page_{page_num}.json"), 'w') as f:
            json.dump(data, f, indent=2)
