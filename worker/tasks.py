from celery import Celery
from celery.schedules import crontab
from transformers import AutoModel, AutoTokenizer
import torch
import os
import shutil
from datetime import datetime, timedelta
# from models import Job, SessionLocal # This will cause circular import
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Database Setup ---
# This needs to be redefined here to avoid circular imports with the web app
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Model Loading ---
# Load DeepSeek-OCR model and tokenizer ONCE globally
MODEL_NAME = "deepseek-ai/DeepSeek-OCR"

model = AutoModel.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    _attn_implementation='flash_attention_2',
    use_safetensors=True
).eval().to("cuda", dtype=torch.bfloat16)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

print("DeepSeek-OCR model loaded on GPU")

# --- Celery App Configuration ---
app = Celery('tasks')
app.config_from_object({
    'broker_url': 'redis://broker:6379/0',
    'result_backend': 'redis://broker:6379/0',
    'task_serializer': 'json',  # SECURITY: Never use pickle
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    'task_track_started': True,
    'task_time_limit': 3600,  # 1 hour max
    'worker_prefetch_multiplier': 1,  # Important for GPU tasks
})

# Scheduled task for cleanup
app.conf.beat_schedule = {
    'cleanup-old-jobs': {
        'task': 'tasks.cleanup_old_jobs',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
}

# --- Document Processor Factory ---
from processors.absence_form import AbsenceFormProcessor
from processors.deduction_sheet import DeductionSheetProcessor
from processors.pod import PODProcessor

PROCESSOR_REGISTRY = {
    'absence_form': AbsenceFormProcessor,
    'deduction_sheet': DeductionSheetProcessor,
    'pod': PODProcessor,
}

def get_processor(document_type):
    """Factory function to get appropriate processor."""
    return PROCESSOR_REGISTRY.get(document_type, AbsenceFormProcessor)()

# --- Main Processing Task ---
@app.task(bind=True)
def process_pdf(self, job_id, pdf_path, document_type='absence_form'):
    """
    Process PDF using DeepSeek-OCR VLM pipeline.
    NO REGEX - pure vision-based extraction.
    """
    # This import needs to be inside the task
    from web.models import Job, JobStatus
    session = SessionLocal()
    
    try:
        # Update job status
        job = session.query(Job).get(job_id)
        job.status = JobStatus.PROCESSING
        job.celery_task_id = self.request.id
        session.commit()
        
        # Get appropriate processor
        processor = get_processor(document_type)
        
        # Load document-specific prompt
        prompt_config = processor.load_prompt_config()
        
        # Create output directories
        output_base = f"/app/data/output/{job_id}"
        os.makedirs(output_base, exist_ok=True)
        
        # Initialize results tracking
        success_data = []
        failed_pages = []
        
        # Convert PDF to images
        from pdf2image import convert_from_path
        pages = convert_from_path(pdf_path, dpi=300)
        
        # Process each page
        for page_num, page_image in enumerate(pages, start=1):
            try:
                # Call DeepSeek-OCR model (NO REGEX!)
                extracted_data = processor.extract_from_image(
                    page_image, 
                    model, 
                    tokenizer, 
                    prompt_config
                )
                
                # Validate extracted data
                if not processor.validate_data(extracted_data):
                    raise ValueError("Critical field missing or invalid")
                
                # Sort and save page to appropriate folder
                processor.save_page(page_image, extracted_data, output_base, page_num)
                
                # Log success
                success_data.append({
                    'page': page_num,
                    **extracted_data
                })
                
            except Exception as e:
                # Move failed page to _FAILED folder
                failed_pages.append(page_num)
                # processor.save_failed_page(page_image, output_base, page_num, str(e))
        
        # Generate Excel report
        # processor.create_master_log(success_data, failed_pages, output_base)
        
        # Create ZIP archive
        zip_path = f"{output_base}.zip"
        shutil.make_archive(output_base, 'zip', output_base)
        
        # Update job as complete
        job.status = JobStatus.COMPLETE
        job.output_zip_path = zip_path
        job.completed_at = datetime.utcnow()
        session.commit()
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        session.commit()
        raise
    finally:
        session.close()

# --- Cleanup Task ---
@app.task
def cleanup_old_jobs():
    """Delete files and DB entries older than 72 hours."""
    from web.models import Job
    session = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(hours=72)
    
    old_jobs = session.query(Job).filter(Job.created_at < cutoff).all()
    
    for job in old_jobs:
        # Delete files
        if job.output_zip_path and os.path.exists(job.output_zip_path):
            shutil.rmtree(os.path.dirname(job.output_zip_path), ignore_errors=True)
        
        # Delete job record
        session.delete(job)
    
    session.commit()
    session.close()
