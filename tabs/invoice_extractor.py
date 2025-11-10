import streamlit as st
import os
import json
import pandas as pd
import zipfile
import shutil
from datetime import datetime
from utils.pdf_handler import convert_pdf_to_images
from utils.chandra_processor import ChandraOCR
from utils.config import TEMP_DIR, OUTPUT_DIR

def invoice_extractor_tab():
    st.header("Invoice Extractor")
    st.write("Upload invoice files (PDF or images) for structured data extraction.")

    uploaded_files = st.file_uploader("Drag and drop your invoices here or click to browse", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        st.subheader("Processing Invoices...")
        
        session_temp_dir = os.path.join(TEMP_DIR, f"invoice_session_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        os.makedirs(session_temp_dir, exist_ok=True)

        ocr_processor = ChandraOCR()
        if not ocr_processor.processor:
            st.error("Failed to initialize OCR processor. Please check logs.")
            shutil.rmtree(session_temp_dir)
            return

        processed_invoices = []
        failed_invoices = []
        
        output_zip_folder = os.path.join(OUTPUT_DIR, f"invoices_output_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        os.makedirs(output_zip_folder, exist_ok=True)
        
        failed_invoices_output_folder = os.path.join(output_zip_folder, "failed_invoices")
        os.makedirs(failed_invoices_output_folder, exist_ok=True)

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name} ({i+1}/{len(uploaded_files)})...")
            progress_bar.progress(int(100 * (i + 1) / len(uploaded_files)))

            file_path = os.path.join(session_temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                image_paths = []
                if uploaded_file.type == "application/pdf":
                    # Convert PDF to images
                    pdf_images_folder = os.path.join(session_temp_dir, f"images_{uploaded_file.name.replace('.', '_')}")
                    os.makedirs(pdf_images_folder, exist_ok=True)
                    image_paths = convert_pdf_to_images(file_path, pdf_images_folder)
                else:
                    image_paths.append(file_path) # Already an image

                if not image_paths:
                    raise ValueError("No images found or generated for processing.")

                extracted_text = ""
                for img_path in image_paths:
                    text = ocr_processor.process_image(img_path)
                    if text:
                        extracted_text += text + "\n"
                
                if not extracted_text.strip():
                    raise ValueError("OCR failed to extract any text.")

                invoice_data = ocr_processor.extract_invoice_data(extracted_text)

                if invoice_data["errors"]:
                    failed_invoices.append({
                        "file_name": uploaded_file.name,
                        "errors": invoice_data["errors"],
                        "raw_text": extracted_text,
                        "file_path": file_path
                    })
                    shutil.copy(file_path, os.path.join(failed_invoices_output_folder, uploaded_file.name))
                    with open(os.path.join(failed_invoices_output_folder, f"{uploaded_file.name}.txt"), "w", encoding="utf-8") as f:
                        f.write(f"Errors: {invoice_data['errors']}\n\nRaw Text:\n{extracted_text}")
                    continue

                processed_invoices.append({
                    "file_name": uploaded_file.name,
                    "data": invoice_data,
                    "raw_text": extracted_text
                })
                
                # Save extracted JSON for individual invoice
                json_output_path = os.path.join(output_zip_folder, f"{uploaded_file.name}.json")
                with open(json_output_path, "w", encoding="utf-8") as f:
                    json.dump(invoice_data, f, indent=4)

            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")
                failed_invoices.append({
                    "file_name": uploaded_file.name,
                    "errors": [str(e)],
                    "raw_text": "N/A",
                    "file_path": file_path
                })
                shutil.copy(file_path, os.path.join(failed_invoices_output_folder, uploaded_file.name))
                with open(os.path.join(failed_invoices_output_folder, f"{uploaded_file.name}.txt"), "w", encoding="utf-8") as f:
                    f.write(f"Errors: {e}\n\nRaw Text: N/A")
                continue

        status_text.text("Processing complete!")
        progress_bar.progress(100)

        st.subheader("Results")
        st.success(f"Successfully processed {len(processed_invoices)} invoices.")
        if failed_invoices:
            st.warning(f"{len(failed_invoices)} invoices failed to process.")

        if processed_invoices:
            st.subheader("Extracted Invoice Data")
            # Display in a DataFrame
            df_data = []
            for inv in processed_invoices:
                row = {"File Name": inv["file_name"]}
                row.update(inv["data"])
                # Flatten line items for display if needed, or show as string
                row["line_items"] = json.dumps(inv["data"].get("line_items", []))
                df_data.append(row)
            
            df = pd.DataFrame(df_data)
            st.dataframe(df)

            # Download options
            st.markdown("---")
            st.subheader("Download Options")

            # JSON Download
            all_invoices_json = json.dumps([inv["data"] for inv in processed_invoices], indent=4)
            st.download_button(
                label="Download All Data as JSON",
                data=all_invoices_json,
                file_name=f"invoices_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.json",
                mime="application/json"
            )

            # CSV Download
            # Create a flattened DataFrame for CSV
            csv_data = []
            for inv in processed_invoices:
                base_data = {k: v for k, v in inv["data"].items() if k != "line_items"}
                if inv["data"].get("line_items"):
                    for item in inv["data"]["line_items"]:
                        row = {"File Name": inv["file_name"]}
                        row.update(base_data)
                        row.update({f"item_{k}": v for k, v in item.items()})
                        csv_data.append(row)
                else:
                    row = {"File Name": inv["file_name"]}
                    row.update(base_data)
                    csv_data.append(row)
            
            if csv_data:
                csv_df = pd.DataFrame(csv_data)
                st.download_button(
                    label="Download All Data as CSV",
                    data=csv_df.to_csv(index=False).encode('utf-8'),
                    file_name=f"invoices_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # ZIP Download (includes individual JSONs and original files)
            zip_file_path = os.path.join(OUTPUT_DIR, f"invoices_output_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip")
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(output_zip_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, output_zip_folder))
                
                # Add original uploaded files to the zip
                for uploaded_file in uploaded_files:
                    original_file_path = os.path.join(session_temp_dir, uploaded_file.name)
                    if os.path.exists(original_file_path):
                        zipf.write(original_file_path, os.path.join("original_uploads", uploaded_file.name))

            with open(zip_file_path, "rb") as f:
                st.download_button(
                    label="Download All Output (ZIP)",
                    data=f.read(),
                    file_name=os.path.basename(zip_file_path),
                    mime="application/zip"
                )

        # Clean up session temporary directory
        shutil.rmtree(session_temp_dir)
        st.success("Temporary files cleaned up.")
