# How to Add a New Document Type

This guide explains how to add a new document processor to the application.

## 1. Create a new Processor Class

Create a new Python file in the `worker/processors` directory (e.g., `worker/processors/new_document_processor.py`).

In this file, create a new class that inherits from `DocumentProcessor` (from `worker/processors/base.py`).

Implement the abstract methods:

- `load_prompt_config(self)`
- `extract_from_image(self, image, model, tokenizer, config)`
- `validate_data(self, data)`
- `save_page(self, image, data, output_base, page_num)`

## 2. Create a new Prompt YAML file

Create a new YAML file in the `worker/prompts` directory (e.g., `worker/prompts/new_document.yaml`).

This file should contain the configuration for the new document type, including:

- `document_type`
- `prompt_template`
- `required_fields`
- `output_folders`
- `sorting_logic`

## 3. Register the new Processor

In `worker/tasks.py`, import your new processor and add it to the `PROCESSOR_REGISTRY` dictionary.

```python
from processors.new_document_processor import NewDocumentProcessor

PROCESSOR_REGISTRY = {
    'absence_form': AbsenceFormProcessor,
    'deduction_sheet': DeductionSheetProcessor,
    'pod': PODProcessor,
    'new_document': NewDocumentProcessor, # Add your new processor here
}
```

## 4. Test the new Processor

Add sample PDFs for the new document type to your testing suite and create unit and integration tests to verify that the new processor works as expected.
