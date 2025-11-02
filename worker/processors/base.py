from abc import ABC, abstractmethod
import yaml

class DocumentProcessor(ABC):
    """Base class for document-specific processors."""
    
    @abstractmethod
    def load_prompt_config(self):
        """Load prompt configuration from YAML file."""
        pass
    
    @abstractmethod
    def extract_from_image(self, image, model, tokenizer, config):
        """Extract data from image using DeepSeek-OCR."""
        pass
    
    @abstractmethod
    def validate_data(self, data):
        """Validate extracted data."""
        pass
    
    @abstractmethod
    def save_page(self, image, data, output_base, page_num):
        """Save processed page to appropriate folder."""
        pass
