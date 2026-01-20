import json
import argparse
import glob
import fitz  # PyMuPDF
from google import genai
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
import config
import os

# Set proxy if specified in config
if config.HTTP_PROXY or config.HTTPS_PROXY:
    os.environ['HTTP_PROXY'] = config.HTTP_PROXY
    os.environ['HTTPS_PROXY'] = config.HTTPS_PROXY

class FigExtractor:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.extraction_prompt = (
            "Analyze this research paper and identify the most representative visual "
            "(e.g., System Architecture, core flowchart, or primary result plot). "
            "Do not include captions or annotations in the selected image. "
            "Return the page number (1-indexed) and normalized coordinates [ymin, xmin, ymax, xmax] "
            "ranging from 0 to 1000. Output MUST be a strict JSON object: "
            '{"page_number": 1, "box_2d": [ymin, xmin, ymax, xmax]}'
        )

    def fetch_image_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Uploads PDF and waits for Gemini to finish processing."""
        uploaded_file = self.client.files.upload(file=pdf_path)
        
        # Poll for completion (Gemini's internal processing)
        while uploaded_file.state.name == "PROCESSING":
            uploaded_file = self.client.files.get(name=uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            raise Exception(f"Gemini processing failed for {pdf_path}")

        response = self.client.models.generate_content(
            model=config.MODEL_NAME,
            contents=[self.extraction_prompt, uploaded_file]
        )
        
        # Cleanup file from cloud
        self.client.files.delete(name=uploaded_file.name)

        raw_text = response.text.strip()
        clean_json = raw_text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)

    def crop_and_save(self, pdf_path: str, info: Dict[str, Any], output_path: str):
        """Extracts and saves the crop."""
        doc = fitz.open(pdf_path)
        page = doc[info['page_number'] - 1]
        
        w_scale = page.rect.width / config.COORDINATE_SCALE
        h_scale = page.rect.height / config.COORDINATE_SCALE

        ymin, xmin, ymax, xmax = info['box_2d']
        fitz_rect = fitz.Rect(xmin * w_scale, ymin * h_scale, xmax * w_scale, ymax * h_scale)

        pix = page.get_pixmap(matrix=fitz.Matrix(config.ZOOM_FACTOR, config.ZOOM_FACTOR), clip=fitz_rect)
        pix.save(output_path)
        doc.close()

def process_single_pdf(pdf_path, extractor, output_arg):
    """Wrapper function for parallel execution."""
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Determine output path
    if output_arg and (os.path.isdir(output_arg) or output_arg.endswith(('/', '\\'))):
        img_path = os.path.join(output_arg, f"{pdf_name}.png")
    elif output_arg:
        img_path = output_arg
    else:
        img_path = os.path.join("images", f"{pdf_name}.png")

    try:
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        metadata = extractor.fetch_image_metadata(pdf_path)
        extractor.crop_and_save(pdf_path, metadata, img_path)
        return True
    except Exception as e:
        # Using tqdm.write to avoid breaking the progress bar
        tqdm.write(f"Error processing {pdf_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Parallel PDF Visual Extractor")
    parser.add_argument("input", help="Input PDF or directory")
    parser.add_argument("-o", "--output", help="Output directory or filename")
    args = parser.parse_args()

    extractor = FigExtractor(config.GEMINI_API_KEY)

    if os.path.isfile(args.input):
        print(f"Processing {args.input}...")
        process_single_pdf(args.input, extractor, args.output)
    elif os.path.isdir(args.input):
        pdf_files = glob.glob(os.path.join(args.input, "*.pdf"))
        if not pdf_files:
            print("No PDF files found.")
            return

        print(f"Starting parallel processing for {len(pdf_files)} files...")
        
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            list(tqdm(executor.map(lambda p: process_single_pdf(p, extractor, args.output), pdf_files), 
                      total=len(pdf_files), desc="Batch Progress"))
    else:
        print("Invalid input path.")

if __name__ == "__main__":
    main()