import os
import pandas as pd
import pdfplumber
from models.local_vlm import LocalVLMProcessor

class DocumentParser:
    def __init__(self):
        # Initialize the VLM as None so it only loads into memory if an image is actually found
        self.vlm_processor = None
        self.temp_image_dir = "uploads/temp_images"
        os.makedirs(self.temp_image_dir, exist_ok=True)

    def parse_file(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.csv':
            return self._parse_csv(filepath)
        elif ext in ['.xls', '.xlsx']:
            return self._parse_excel(filepath)
        elif ext == '.pdf':
            return self._parse_pdf(filepath)
        elif ext in ['.png', '.jpg', '.jpeg']:
            if not self.vlm_processor:
                print("Direct image upload detected. Loading local VLM into CPU memory...")
                self.vlm_processor = LocalVLMProcessor()
            return f"Image Data Insights:\n{self.vlm_processor.analyze_image(filepath)}"
        else:
            return f"Unsupported file type: {ext}."

    def _parse_csv(self, filepath):
        df = pd.read_csv(filepath)
        return f"CSV Data:\n{df.head(15).to_string()}\nColumns: {list(df.columns)}"

    def _parse_excel(self, filepath):
        df = pd.read_excel(filepath)
        return f"Excel Data:\n{df.head(15).to_string()}\nColumns: {list(df.columns)}"

    def _parse_pdf(self, filepath):
        text_content = ""
        with pdfplumber.open(filepath) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_content += f"\n--- Page {i+1} Text ---\n{text}"
                
                # Image Extraction & Custom VLM Processing
                if page.images:
                    if not self.vlm_processor:
                        print("Image detected. Loading local VLM into CPU memory...")
                        self.vlm_processor = LocalVLMProcessor()
                    
                    for j, img in enumerate(page.images):
                        # Calculate bounding box and crop the image from the PDF page
                        bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                        cropped_img = page.crop(bbox).to_image(resolution=300)
                        
                        img_path = os.path.join(self.temp_image_dir, f"page_{i}_img_{j}.png")
                        cropped_img.save(img_path)
                        
                        # Send to your local CPU VLM
                        print(f"Processing diagram {j} on page {i+1}...")
                        img_description = self.vlm_processor.analyze_image(img_path)
                        text_content += f"\n--- Page {i+1} Diagram {j} Insights ---\n{img_description}\n"
                        
        return text_content