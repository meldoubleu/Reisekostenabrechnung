"""
Test OCR functionality with real receipt images.
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.app.services.ocr import extract_text_from_file, simple_parse
from tests.test_data_manager import test_data_manager
import tempfile
import os
from pathlib import Path


class TestOCR:
    """Test OCR service functionality with real receipt images."""
    
    @classmethod
    def setup_class(cls):
        """Set up test data before running tests."""
        # Generate synthetic receipts for testing
        cls.test_files = test_data_manager.generate_synthetic_receipts()
        # Also try to get any downloaded files
        cls.test_files.update(test_data_manager.get_all_files())
    
    def test_simple_parse_restaurant_receipt(self):
        """Test parsing restaurant receipt text for structured data."""
        restaurant_text = """
        CAFE BISTRO BERLIN
        Unter den Linden 123
        10117 Berlin
        
        Date: 2025-01-15
        Time: 12:30:45
        Table: 7
        
        1x Espresso          €2.50
        1x Cappuccino        €3.20
        1x Club Sandwich     €8.50
        1x Caesar Salad      €7.80
        2x Mineral Water     €5.00
        
        Subtotal:          €27.00
        VAT (19%):          €5.13
        TOTAL:             €32.13
        
        Payment: Credit Card
        Thank you!
        """
        
        result = simple_parse(restaurant_text)
        
        assert isinstance(result, dict)
        # Should extract amount, merchant, or date
        assert any(key in result and result[key] is not None 
                  for key in ["amount", "merchant", "date"])
    
    def test_simple_parse_hotel_receipt(self):
        """Test parsing hotel receipt text."""
        hotel_text = """
        GRAND HOTEL BERLIN
        Kurfuerstendamm 123
        10719 Berlin, Germany
        
        GUEST RECEIPT
        Guest: Max Mustermann
        Room: 205 (Superior)
        Check-in: 2025-01-10 15:00
        Check-out: 2025-01-12 11:00
        
        CHARGES:
        Room (2 nights)    €180.00
        Breakfast (2x)      €30.00
        City Tax             €6.00
        
        Subtotal:          €216.00
        VAT (19%):          €41.04
        TOTAL:             €257.04
        
        Payment: Credit Card
        """
        
        result = simple_parse(hotel_text)
        
        assert isinstance(result, dict)
        # Should extract some structured data
        assert any(key in result and result[key] is not None 
                  for key in ["amount", "merchant", "date"])
    
    def test_simple_parse_taxi_receipt(self):
        """Test parsing taxi receipt text."""
        taxi_text = """
        CITY CAB COMPANY
        License: TX-123456
        Driver: Hans Mueller
        
        TAXI RECEIPT
        Date: 2025-01-14
        Time: 16:45 - 17:10
        
        From: Airport Terminal 1
        To: Hotel Downtown
        
        Distance: 12.5 km
        Duration: 25 minutes
        
        Base Fare:     €4.50
        Distance:     €12.50
        Time:          €1.50
        Tip:           €2.00
        
        TOTAL:        €20.50
        
        Payment: Credit Card
        """
        
        result = simple_parse(taxi_text)
        
        assert isinstance(result, dict)
        assert any(key in result and result[key] is not None 
                  for key in ["amount", "merchant", "date"])
    
    def test_simple_parse_empty_text(self):
        """Test parsing empty or invalid text."""
        result = simple_parse("")
        assert isinstance(result, dict)
        
        result = simple_parse(None)
        assert isinstance(result, dict)
    
    @patch('backend.app.services.ocr.pytesseract.image_to_string')
    def test_extract_text_from_real_receipt_image(self, mock_ocr):
        """Test extracting text from a real receipt image."""
        # Mock OCR to return realistic receipt text
        mock_ocr.return_value = """
        CAFE BISTRO BERLIN
        Unter den Linden 123
        10117 Berlin
        
        Date: 2025-01-15
        Time: 12:30:45
        
        1x Espresso          €2.50
        1x Cappuccino        €3.20
        1x Club Sandwich     €8.50
        
        TOTAL:             €14.20
        """
        
        # Use one of our generated test images
        if "synthetic_restaurant" in self.test_files:
            image_path = self.test_files["synthetic_restaurant"]
            result = extract_text_from_file(str(image_path))
            
            assert isinstance(result, str)
            assert len(result) > 0
            mock_ocr.assert_called_once()
        else:
            pytest.skip("No restaurant test image available")
    
    @patch('backend.app.services.ocr.pytesseract.image_to_string')
    def test_extract_text_from_hotel_receipt_image(self, mock_ocr):
        """Test extracting text from a hotel receipt image."""
        mock_ocr.return_value = """
        GRAND HOTEL BERLIN
        Kurfuerstendamm 123
        
        Guest: Max Mustermann
        Room: 205
        
        Room (2 nights)    €180.00
        Breakfast (2x)      €30.00
        TOTAL:             €210.00
        """
        
        if "synthetic_hotel" in self.test_files:
            image_path = self.test_files["synthetic_hotel"]
            result = extract_text_from_file(str(image_path))
            
            assert isinstance(result, str)
            assert len(result) > 0
            mock_ocr.assert_called_once()
        else:
            pytest.skip("No hotel test image available")
    
    @patch('backend.app.services.ocr.pytesseract.image_to_string')
    def test_extract_text_from_taxi_receipt_image(self, mock_ocr):
        """Test extracting text from a taxi receipt image."""
        mock_ocr.return_value = """
        CITY CAB COMPANY
        License: TX-123456
        
        From: Airport
        To: Hotel Downtown
        Distance: 12.5 km
        TOTAL: €20.50
        """
        
        if "synthetic_taxi" in self.test_files:
            image_path = self.test_files["synthetic_taxi"]
            result = extract_text_from_file(str(image_path))
            
            assert isinstance(result, str)
            assert len(result) > 0
            mock_ocr.assert_called_once()
        else:
            pytest.skip("No taxi test image available")
    
    @patch('backend.app.services.ocr.convert_from_path')
    @patch('backend.app.services.ocr.pytesseract.image_to_string')
    def test_extract_text_from_pdf_receipt(self, mock_ocr, mock_pdf_convert):
        """Test extracting text from a PDF receipt."""
        # Mock PDF conversion and OCR
        mock_image = MagicMock()
        mock_pdf_convert.return_value = [mock_image]
        mock_ocr.return_value = """
        INVOICE
        Company ABC GmbH
        
        Invoice Date: 2025-01-15
        Due Date: 2025-02-14
        
        Service: Consulting     €500.00
        VAT (19%):             €95.00
        TOTAL:                 €595.00
        """
        
        # Use the simple PDF we downloaded
        pdf_files = [f for f in self.test_files.values() if str(f).endswith('.pdf')]
        if pdf_files:
            pdf_path = pdf_files[0]
            result = extract_text_from_file(str(pdf_path))
            
            assert isinstance(result, str)
            assert len(result) > 0
            mock_pdf_convert.assert_called_once_with(str(pdf_path))
            mock_ocr.assert_called_once()
        else:
            pytest.skip("No PDF test file available")
    
    def test_extract_text_from_nonexistent_file(self):
        """Test extracting text from a file that doesn't exist."""
        result = extract_text_from_file("/nonexistent/file.jpg")
        
        # Should return empty string when file doesn't exist
        assert result == ""
    
    def test_simple_parse_various_receipt_formats(self):
        """Test parsing various receipt formats."""
        receipt_formats = [
            # German receipt format
            {
                "text": """
                LIDL DEUTSCHLAND
                Filiale 1234
                Musterstraße 123
                12345 Berlin
                
                Datum: 15.01.2025
                Uhrzeit: 14:30
                
                Milch 1,5%           1,89 €
                Brot                 0,89 €
                Äpfel 1kg            2,99 €
                
                Zwischensumme:       5,77 €
                MwSt 7%:             0,40 €
                SUMME:               6,17 €
                
                Gegeben:            10,00 €
                Rückgeld:            3,83 €
                """,
                "expected_keys": ["amount", "merchant"]
            },
            # US receipt format
            {
                "text": """
                WALMART SUPERCENTER
                Store #1234
                123 Main Street
                Anytown, NY 12345
                
                Date: 01/15/2025
                Time: 2:30 PM
                
                Milk 1 Gallon        $3.98
                Bread                $1.28
                Apples 3 lbs         $4.97
                
                Subtotal:           $10.23
                Tax:                 $0.82
                TOTAL:              $11.05
                
                VISA Card Payment
                """,
                "expected_keys": ["amount", "merchant"]
            },
            # UK receipt format
            {
                "text": """
                TESCO EXPRESS
                Store 4567
                Oxford Street 456
                London W1A 1AB
                
                Date: 15/01/2025
                Time: 14:30
                
                Milk 2 Pints         £1.25
                Bread Loaf           £0.85
                Bananas 1kg          £1.10
                
                Subtotal:            £3.20
                VAT:                 £0.64
                TOTAL:               £3.84
                
                Contactless Payment
                """,
                "expected_keys": ["amount", "merchant"]
            }
        ]
        
        for i, receipt_data in enumerate(receipt_formats):
            result = simple_parse(receipt_data["text"])
            
            assert isinstance(result, dict), f"Failed for receipt format {i+1}"
            
            # Check if at least one expected key is present and has a value
            found_keys = [key for key in receipt_data["expected_keys"] 
                         if key in result and result[key] is not None]
            assert len(found_keys) > 0, f"No expected keys found in receipt format {i+1}"
    
    @classmethod
    def teardown_class(cls):
        """Clean up test data after running tests."""
        # Optionally clean up test files
        pass  # Keep files for inspection during development
