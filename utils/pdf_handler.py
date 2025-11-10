import os
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image

def split_pdf(pdf_path, output_folder):
    """
    Splits a multi-page PDF into individual PDF files, one page per file.
    Returns a list of paths to the split PDF files.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    reader = PdfReader(pdf_path)
    split_pdf_paths = []
    for i in range(len(reader.pages)):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        output_path = os.path.join(output_folder, f"page_{i+1}.pdf")
        with open(output_path, "wb") as output_pdf:
            writer.write(output_pdf)
        split_pdf_paths.append(output_path)
    return split_pdf_paths

def convert_pdf_to_images(pdf_path, output_folder, dpi=300):
    """
    Converts each page of a PDF into a high-resolution image.
    Returns a list of paths to the generated image files.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    for i, image in enumerate(images):
        output_image_path = os.path.join(output_folder, f"page_{i+1}.png")
        image.save(output_image_path, "PNG")
        image_paths.append(output_image_path)
    return image_paths

def get_pdf_page_count(pdf_path):
    """
    Returns the number of pages in a PDF file.
    """
    reader = PdfReader(pdf_path)
    return len(reader.pages)