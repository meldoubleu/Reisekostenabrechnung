"""
Receipt parsing service for extracting structured data from images/PDFs.
This module will handle OCR, AI parsing, and data extraction.
"""
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import re
import logging
from pathlib import Path

from ..schemas.travel import ReceiptParsed, ExpenseCategory


logger = logging.getLogger(__name__)


class ReceiptParsingService:
    """Service for parsing receipt images/PDFs into structured data."""
    
    def __init__(self):
        self.confidence_threshold = 70.0  # Minimum confidence for auto-categorization
        
    async def parse_receipt_file(self, file_path: str, mime_type: str) -> ReceiptParsed:
        """
        Parse a receipt file and extract structured data.
        
        Args:
            file_path: Path to the receipt file
            mime_type: MIME type of the file
            
        Returns:
            ReceiptParsed object with extracted data
        """
        try:
            # Step 1: Extract text using OCR
            ocr_text = await self._extract_text_ocr(file_path, mime_type)
            
            # Step 2: Parse structured data from OCR text
            parsed_data = await self._parse_text_to_fields(ocr_text)
            
            # Step 3: Auto-categorize based on merchant/content
            category = await self._auto_categorize(parsed_data, ocr_text)
            parsed_data["category"] = category
            
            # Step 4: Calculate confidence score
            confidence = self._calculate_confidence(parsed_data, ocr_text)
            
            return ReceiptParsed(
                **parsed_data,
                parsing_confidence=confidence,
                ocr_text=ocr_text
            )
            
        except Exception as e:
            logger.error(f"Failed to parse receipt {file_path}: {str(e)}")
            return ReceiptParsed(
                parsing_confidence=0.0,
                ocr_text=f"Parsing failed: {str(e)}"
            )
    
    async def _extract_text_ocr(self, file_path: str, mime_type: str) -> str:
        """Extract text from image/PDF using OCR."""
        # TODO: Implement OCR using Tesseract or cloud OCR service
        # For now, return placeholder
        logger.info(f"OCR extraction for {file_path} ({mime_type})")
        
        # Placeholder OCR text for testing
        return """
        HOTEL BERLIN
        Friedrichstraße 123
        10117 Berlin
        
        Rechnung Nr: 2024-001234
        Datum: 15.01.2024
        
        Übernachtung Business Room   87,50 €
        MwSt. 19%                    14,01 €
        Gesamt                      101,51 €
        
        Zahlung: EC-Karte
        USt-IdNr: DE123456789
        """
    
    async def _parse_text_to_fields(self, ocr_text: str) -> Dict[str, Any]:
        """Parse OCR text to extract structured fields."""
        parsed = {}
        
        # Extract amount (look for total/gesamt)
        amount_match = re.search(r'(?:gesamt|total|summe)[:\s]*([0-9,]+[.,][0-9]{2})', 
                               ocr_text.lower())
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '.')
            parsed["amount"] = float(amount_str)
        
        # Extract VAT
        vat_match = re.search(r'mwst[.\s]*([0-9]+)%[:\s]*([0-9,]+[.,][0-9]{2})', 
                            ocr_text.lower())
        if vat_match:
            parsed["vat_rate"] = float(vat_match.group(1))
            vat_str = vat_match.group(2).replace(',', '.')
            parsed["vat"] = float(vat_str)
        
        # Extract date
        date_match = re.search(r'datum[:\s]*([0-9]{1,2}[./][0-9]{1,2}[./][0-9]{2,4})', 
                             ocr_text.lower())
        if date_match:
            date_str = date_match.group(1)
            try:
                # Try different date formats
                for fmt in ['%d.%m.%Y', '%d/%m/%Y', '%d.%m.%y']:
                    try:
                        parsed["date"] = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
            except ValueError:
                pass
        
        # Extract merchant (usually first line or after specific keywords)
        lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
        if lines:
            # Take first non-empty line as potential merchant name
            parsed["merchant"] = lines[0]
        
        # Extract invoice number
        invoice_match = re.search(r'(?:rechnung|invoice|nr)[.\s#]*([a-z0-9-]+)', 
                                ocr_text.lower())
        if invoice_match:
            parsed["invoice_number"] = invoice_match.group(1)
        
        # Extract payment method
        payment_patterns = [
            r'ec-karte',
            r'kreditkarte', 
            r'bargeld',
            r'überweisung',
            r'paypal'
        ]
        for pattern in payment_patterns:
            if re.search(pattern, ocr_text.lower()):
                parsed["payment_method"] = pattern.replace('-', '_')
                break
        
        # Set currency (default EUR for German receipts)
        parsed["currency"] = "EUR"
        
        return parsed
    
    async def _auto_categorize(self, parsed_data: Dict[str, Any], ocr_text: str) -> Optional[ExpenseCategory]:
        """Auto-categorize receipt based on merchant and content."""
        ocr_lower = ocr_text.lower()
        merchant = parsed_data.get("merchant", "").lower()
        
        # Hotel/Accommodation keywords
        hotel_keywords = ['hotel', 'hostel', 'pension', 'übernachtung', 'accommodation', 'zimmer']
        if any(keyword in merchant or keyword in ocr_lower for keyword in hotel_keywords):
            return ExpenseCategory.lodging
        
        # Transport keywords
        transport_keywords = ['bahn', 'flug', 'airline', 'taxi', 'uber', 'bus', 'ticket', 'fahrkarte']
        if any(keyword in merchant or keyword in ocr_lower for keyword in transport_keywords):
            return ExpenseCategory.transport
        
        # Restaurant/Meals keywords
        meal_keywords = ['restaurant', 'café', 'bar', 'pizza', 'mcdonalds', 'burger', 'bistro', 'essen']
        if any(keyword in merchant or keyword in ocr_lower for keyword in meal_keywords):
            return ExpenseCategory.meals
        
        # Entertainment keywords
        entertainment_keywords = ['kino', 'theater', 'museum', 'ticket', 'event', 'konzert']
        if any(keyword in merchant or keyword in ocr_lower for keyword in entertainment_keywords):
            return ExpenseCategory.entertainment
        
        # Default to other if no clear category
        return ExpenseCategory.other
    
    def _calculate_confidence(self, parsed_data: Dict[str, Any], ocr_text: str) -> float:
        """Calculate confidence score for parsed data."""
        confidence = 0.0
        
        # Base confidence if we have any data
        if parsed_data:
            confidence = 30.0
        
        # Boost confidence for key fields
        if parsed_data.get("amount"):
            confidence += 25.0
        if parsed_data.get("merchant"):
            confidence += 20.0
        if parsed_data.get("date"):
            confidence += 15.0
        if parsed_data.get("vat"):
            confidence += 10.0
        
        # OCR text quality indicators
        if len(ocr_text) > 100:  # Reasonable amount of text
            confidence += 5.0
        if re.search(r'[0-9,]+[.,][0-9]{2}', ocr_text):  # Contains price patterns
            confidence += 5.0
        
        return min(confidence, 100.0)


# Global service instance
receipt_parser = ReceiptParsingService()
