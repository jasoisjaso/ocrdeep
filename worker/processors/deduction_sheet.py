from .base import DocumentProcessor

class DeductionSheetProcessor(DocumentProcessor):
    def load_prompt_config(self):
        # To be implemented
        pass

    def extract_from_image(self, image, model, tokenizer, config):
        # To be implemented
        pass

    def validate_data(self, data):
        # To be implemented
        return True

    def save_page(self, image, data, output_base, page_num):
        # To be implemented
        pass
