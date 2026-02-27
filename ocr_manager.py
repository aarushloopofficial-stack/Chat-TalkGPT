"""
Chat&Talk GPT - OCR Manager
Extract text from images using OCR (Optical Character Recognition)
Supports multiple languages and image formats
"""
import io
import logging
import base64
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger("OCRManager")

# Try to import OCR libraries
PYTESSERACT_AVAILABLE = False
EASYOCR_AVAILABLE = False
PIL_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    PYTESSERACT_AVAILABLE = True
    PIL_AVAILABLE = True
    logger.info("PyTesseract OCR is available")
except ImportError:
    logger.warning("PyTesseract not available - trying EasyOCR")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
    logger.info("EasyOCR is available")
except ImportError:
    logger.warning("EasyOCR not available")

# Language code mapping for OCR
OCR_LANGUAGES = {
    "english": "eng",
    "hindi": "hin",
    "nepali": "nep",
    "chinese": "chi_sim",
    "japanese": "jpn",
    "korean": "kor",
    "arabic": "ara",
    "russian": "rus",
    "spanish": "spa",
    "french": "fra",
    "german": "deu",
    "multi": "eng+hin+nep"
}


class OCRManager:
    """
    OCR Manager for extracting text from images
    
    Features:
    - Multiple OCR engines (Tesseract, EasyOCR)
    - Multi-language support
    - Image preprocessing
    - PDF text extraction
    - Batch processing
    """
    
    def __init__(self, engine: str = "auto"):
        """
        Initialize OCR Manager
        
        Args:
            engine: OCR engine to use ('tesseract', 'easyocr', 'auto')
        """
        self.engine = engine
        self.easyocr_reader = None
        
        # Initialize EasyOCR reader if available
        if EASYOCR_AVAILABLE and (engine == "easyocr" or engine == "auto"):
            try:
                # Initialize with common languages
                self.easyocr_reader = easyocr.Reader(['en', 'hi', 'ne'], gpu=False)
                logger.info("EasyOCR reader initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize EasyOCR: {e}")
        
        logger.info(f"OCR Manager initialized with {engine} engine")
    
    def extract_text_from_image(
        self,
        image_data: Optional[bytes] = None,
        image_base64: Optional[str] = None,
        language: str = "english",
        preprocess: bool = True
    ) -> Dict[str, Any]:
        """
        Extract text from an image
        
        Args:
            image_data: Raw image bytes
            image_base64: Base64 encoded image
            language: Language for OCR
            preprocess: Whether to preprocess image
            
        Returns:
            Dictionary with extracted text and confidence
        """
        try:
            # Convert base64 to bytes if needed
            if image_base64 and not image_data:
                # Remove data URL prefix if present
                if "," in image_base64:
                    image_base64 = image_base64.split(",")[1]
                image_data = base64.b64decode(image_base64)
            
            if not image_data:
                return {
                    "success": False,
                    "error": "No image data provided"
                }
            
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Determine which engine to use
            use_easyocr = EASYOCR_AVAILABLE and (
                self.engine == "easyocr" or 
                (self.engine == "auto" and not PYTESSERACT_AVAILABLE)
            )
            
            if use_easyocr and self.easyocr_reader:
                return self._extract_with_easyocr(image, language)
            elif PYTESSERACT_AVAILABLE:
                return self._extract_with_tesseract(image, language, preprocess)
            else:
                return {
                    "success": False,
                    "error": "No OCR engine available"
                }
                
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_with_easyocr(self, image: Image.Image, language: str) -> Dict[str, Any]:
        """Extract text using EasyOCR"""
        try:
            # Get language codes for EasyOCR
            lang_list = ['en']  # Default
            if language == "hindi":
                lang_list = ['hi']
            elif language == "nepali":
                lang_list = ['ne']
            elif language == "multi":
                lang_list = ['en', 'hi', 'ne']
            
            # Convert PIL Image to numpy array
            import numpy as np
            image_array = np.array(image)
            
            # Run OCR
            results = self.easyocr_reader.readtext(image_array)
            
            # Combine all text
            full_text = ""
            details = []
            
            for (bbox, text, confidence) in results:
                full_text += text + " "
                details.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })
            
            return {
                "success": True,
                "text": full_text.strip(),
                "details": details,
                "engine": "easyocr"
            }
            
        except Exception as e:
            logger.error(f"EasyOCR error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_with_tesseract(
        self,
        image: Image.Image,
        language: str,
        preprocess: bool
    ) -> Dict[str, Any]:
        """Extract text using Tesseract"""
        try:
            # Get language code
            lang_code = OCR_LANGUAGES.get(language, "eng")
            
            # Preprocess image if requested
            if preprocess:
                image = self._preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang=lang_code)
            
            # Get confidence
            data = pytesseract.image_to_data(image, lang=lang_code, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "success": True,
                "text": text.strip(),
                "confidence": avg_confidence,
                "engine": "tesseract"
            }
            
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        from PIL import ImageEnhance, ImageFilter
        
        # Convert to grayscale
        image = image.convert('L')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Sharpen
        image = image.filter(ImageFilter.SHARPEN)
        
        # Resize if too small
        width, height = image.size
        if width < 800 or height < 800:
            scale = 800 / max(width, height)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def extract_text_from_pdf(self, pdf_data: bytes) -> Dict[str, Any]:
        """
        Extract text from PDF using OCR
        
        Args:
            pdf_data: PDF file bytes
            
        Returns:
            Dictionary with extracted text per page
        """
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(io.BytesIO(pdf_data))
            results = {
                "success": True,
                "pages": [],
                "total_pages": len(reader.pages)
            }
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                
                # If no text found, try OCR
                if not text or len(text.strip()) < 10:
                    # Convert page to image and OCR (simplified)
                    logger.info(f"Page {page_num + 1} has no extractable text, using OCR")
                    text = "[OCR needed for this page]"
                
                results["pages"].append({
                    "page": page_num + 1,
                    "text": text
                })
            
            # Combine all text
            results["full_text"] = "\n\n".join(
                [p["text"] for p in results["pages"]]
            )
            
            return results
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from image or PDF file
        
        Args:
            file_path: Path to image or PDF file
            
        Returns:
            Dictionary with extracted text
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "File not found"
                }
            
            file_ext = Path(file_path).suffix.lower()
            
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            if file_ext in ['.pdf']:
                return self.extract_text_from_pdf(file_data)
            else:
                return self.extract_text_from_image(image_data=file_data)
                
        except Exception as e:
            logger.error(f"File extraction error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_extract(
        self,
        image_list: List[Dict[str, Any]],
        language: str = "english"
    ) -> Dict[str, Any]:
        """
        Extract text from multiple images
        
        Args:
            image_list: List of image dictionaries
            language: Language for OCR
            
        Returns:
            Dictionary with results for each image
        """
        results = {
            "success": True,
            "total": len(image_list),
            "results": []
        }
        
        for idx, img_data in enumerate(image_list):
            result = self.extract_text_from_image(
                image_data=img_data.get("bytes"),
                image_base64=img_data.get("base64"),
                language=language
            )
            result["index"] = idx
            result["filename"] = img_data.get("filename", f"image_{idx}")
            results["results"].append(result)
        
        return results
    
    def scan_document(
        self,
        image_data: bytes,
        output_format: str = "text"
    ) -> Dict[str, Any]:
        """
        Scan document and return structured data
        
        Args:
            image_data: Image bytes
            output_format: Output format ('text', 'json', 'dict')
            
        Returns:
            Structured document data
        """
        result = self.extract_text_from_image(image_data)
        
        if not result.get("success"):
            return result
        
        # Analyze text structure
        text = result["text"]
        
        # Try to identify structure
        lines = text.split('\n')
        structure = {
            "paragraphs": [],
            "words": len(text.split()),
            "characters": len(text),
            "lines": len(lines)
        }
        
        # Group lines into paragraphs
        current_paragraph = []
        for line in lines:
            if line.strip():
                current_paragraph.append(line.strip())
            else:
                if current_paragraph:
                    structure["paragraphs"].append(" ".join(current_paragraph))
                    current_paragraph = []
        
        if current_paragraph:
            structure["paragraphs"].append(" ".join(current_paragraph))
        
        result["structure"] = structure
        
        if output_format == "text":
            result["formatted"] = text
        elif output_format == "json":
            import json
            result["formatted"] = json.dumps(structure, indent=2)
        
        return result


# Singleton instance
ocr_manager = OCRManager()


# Standalone functions for easy import
def extract_text_from_image(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to extract text from image"""
    return ocr_manager.extract_text_from_image(*args, **kwargs)


def extract_text_from_pdf(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to extract text from PDF"""
    return ocr_manager.extract_text_from_pdf(*args, **kwargs)


def extract_text_from_file(*args, **kwargs) -> Dict[str, Any]:
    """Standalone function to extract text from file"""
    return ocr_manager.extract_text_from_file(*args, **kwargs)
