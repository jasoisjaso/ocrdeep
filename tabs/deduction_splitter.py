import streamlit as st
import os
import zipfile
import shutil
from datetime import datetime
from utils.pdf_handler import split_pdf, convert_pdf_to_images, get_pdf_page_count
from utils.chandra_processor import ChandraOCR
from utils.config import TEMP_DIR, OUTPUT_DIR, PIN_PREFIX_MAPPING

def deduction_splitter_tab():
    st.header("Deduction Form Splitter")
    st.write("Upload a PDF containing multiple deduction forms. Each page should represent one form.")

    uploaded_file = st.file_uploader("Drag and drop your PDF here or click to browse", type=["pdf"])

    if uploaded_file:
        st.subheader("Processing PDF...")
        
        # Create a temporary directory for this upload
        session_temp_dir = os.path.join(TEMP_DIR, f"deduction_session_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        os.makedirs(session_temp_dir, exist_ok=True)
        
        input_pdf_path = os.path.join(session_temp_dir, uploaded_file.name)
        with open(input_pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        total_pages = get_pdf_page_count(input_pdf_path)
        st.info(f"Detected {total_pages} pages in the PDF.")

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Initialize OCR processor
        ocr_processor = ChandraOCR()
        if not ocr_processor.processor:
            st.error("Failed to initialize OCR processor. Please check logs.")
            shutil.rmtree(session_temp_dir)
            return

        # Split PDF into individual pages
        status_text.text("Splitting PDF into individual pages...")
        split_pdfs_folder = os.path.join(session_temp_dir, "split_pdfs")
        split_pdf_paths = split_pdf(input_pdf_path, split_pdfs_folder)
        progress_bar.progress(10)

        processed_forms = []
        failed_forms = []
        
        output_zip_folder = os.path.join(OUTPUT_DIR, f"deduction_forms_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        os.makedirs(output_zip_folder, exist_ok=True)
        
        failed_forms_output_folder = os.path.join(output_zip_folder, "failed_forms")
        os.makedirs(failed_forms_output_folder, exist_ok=True)

        for i, page_pdf_path in enumerate(split_pdf_paths):
            status_text.text(f"Processing page {i+1}/{total_pages}...")
            progress_bar.progress(10 + int(80 * (i + 1) / total_pages))

            try:
                # Convert page PDF to image for OCR
                page_images_folder = os.path.join(session_temp_dir, f"page_{i+1}_images")
                os.makedirs(page_images_folder, exist_ok=True)
                image_paths = convert_pdf_to_images(page_pdf_path, page_images_folder)
                
                if not image_paths:
                    raise ValueError("No images generated from PDF page.")
                
                # Assuming one image per page
                image_path = image_paths[0] 

                # Perform OCR
                extracted_text = ocr_processor.process_image(image_path)
                if not extracted_text:
                    raise ValueError("OCR failed to extract text from image.")

                # Extract data
                deduction_data = ocr_processor.extract_deduction_data(extracted_text)

                if deduction_data["errors"]:
                    failed_forms.append({
                        "page": i + 1,
                        "original_file": uploaded_file.name,
                        "errors": deduction_data["errors"],
                        "raw_text": extracted_text,
                        "pdf_path": page_pdf_path # Keep path to original page for failed forms
                    })
                    # Move the failed PDF page to the failed forms folder
                    shutil.copy(page_pdf_path, os.path.join(failed_forms_output_folder, f"page_{i+1}_failed.pdf"))
                    with open(os.path.join(failed_forms_output_folder, f"page_{i+1}_failed.txt"), "w", encoding="utf-8") as f:
                        f.write(f"Errors: {deduction_data['errors']}\n\nRaw Text:\n{extracted_text}")
                    continue

                # Determine output path
                company_folder = deduction_data.get("company", "Unknown Company").replace(" ", "_")
                form_type_folder = deduction_data.get("form_type", "Unknown_Form_Type")
                name = deduction_data.get("name", "Unknown_Name").replace(" ", "_")
                date = deduction_data.get("date", datetime.now().strftime("%Y%m%d"))
                
                # Clean up date for filename if it contains slashes or dots
                date_for_filename = date.replace("/", "").replace(".", "")

                output_filename = f"{name}_{date_for_filename}_{form_type_folder}.pdf"
                
                final_output_path_dir = os.path.join(output_zip_folder, company_folder, form_type_folder)
                os.makedirs(final_output_path_dir, exist_ok=True)
                
                final_output_path = os.path.join(final_output_path_dir, output_filename)
                shutil.copy(page_pdf_path, final_output_path)
                
                processed_forms.append({
                    "page": i + 1,
                    "name": deduction_data["name"],
                    "pin": deduction_data["pin"],
                    "date": deduction_data["date"],
                    "form_type": deduction_data["form_type"],
                    "company": deduction_data["company"],
                    "output_path": final_output_path
                })

            except Exception as e:
                st.error(f"Error processing page {i+1}: {e}")
                failed_forms.append({
                    "page": i + 1,
                    "original_file": uploaded_file.name,
                    "errors": [str(e)],
                    "raw_text": "N/A",
                    "pdf_path": page_pdf_path
                })
                shutil.copy(page_pdf_path, os.path.join(failed_forms_output_folder, f"page_{i+1}_failed.pdf"))
                with open(os.path.join(failed_forms_output_folder, f"page_{i+1}_failed.txt"), "w", encoding="utf-8") as f:
                    f.write(f"Errors: {e}\n\nRaw Text: N/A")
                continue

        progress_bar.progress(100)
        status_text.text("Processing complete!")

        st.subheader("Results")
        st.success(f"Successfully processed {len(processed_forms)} forms.")
        if failed_forms:
            st.warning(f"{len(failed_forms)} forms failed to process.")

        if processed_forms:
            st.subheader("Processed Forms Details")
            for form in processed_forms:
                with st.expander(f"Page {form['page']}: {form['name']} - {form['form_type']}"):
                    st.json(form)

        if failed_forms:
            st.subheader("Failed Forms Details")
            for form in failed_forms:
                with st.expander(f"Page {form['page']}: {form['original_file']}"):
                    st.json(form)
                    
        # Create ZIP file for download
        zip_file_path = os.path.join(OUTPUT_DIR, f"deduction_forms_output_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip")
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(output_zip_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Ensure the path inside the zip is relative to the output_zip_folder
                    zipf.write(file_path, os.path.relpath(file_path, output_zip_folder))

        with open(zip_file_path, "rb") as f:
            st.download_button(
                label="Download Processed Forms (ZIP)",
                data=f.read(),
                file_name=os.path.basename(zip_file_path),
                mime="application/zip"
            )
        
        # Clean up session temporary directory
        shutil.rmtree(session_temp_dir)
        st.success("Temporary files cleaned up.")
