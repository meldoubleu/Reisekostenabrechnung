"""
Test the receipt parsing service functionality.
"""
import pytest
import asyncio
from backend.app.services.receipt_parsing import receipt_parser


class TestReceiptParsing:
    """Test receipt parsing functionality."""
    
    @pytest.mark.asyncio
    async def test_parse_text_to_fields(self):
        """Test parsing structured data from OCR text."""
        # Sample OCR text (German hotel receipt)
        ocr_text = """
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
        
        parsed = await receipt_parser._parse_text_to_fields(ocr_text)
        
        # Test extracted fields
        assert parsed["amount"] == 101.51
        assert parsed["vat"] == 14.01
        assert parsed["vat_rate"] == 19.0
        assert parsed["merchant"] == "HOTEL BERLIN"
        assert parsed["invoice_number"] == "2024-001234"
        assert parsed["payment_method"] == "ec_karte"
        assert parsed["currency"] == "EUR"
        assert parsed["date"] is not None
    
    @pytest.mark.asyncio
    async def test_auto_categorize_hotel(self):
        """Test auto-categorization for hotel receipts."""
        parsed_data = {"merchant": "Hotel Berlin"}
        ocr_text = "HOTEL BERLIN Übernachtung Business Room"
        
        category = await receipt_parser._auto_categorize(parsed_data, ocr_text)
        
        assert category.value == "lodging"
    
    @pytest.mark.asyncio
    async def test_auto_categorize_restaurant(self):
        """Test auto-categorization for restaurant receipts."""
        parsed_data = {"merchant": "Restaurant ABC"}
        ocr_text = "Restaurant ABC Pizza Margherita"
        
        category = await receipt_parser._auto_categorize(parsed_data, ocr_text)
        
        assert category.value == "meals"
    
    @pytest.mark.asyncio
    async def test_auto_categorize_transport(self):
        """Test auto-categorization for transport receipts."""
        parsed_data = {"merchant": "Deutsche Bahn"}
        ocr_text = "Deutsche Bahn Fahrkarte ICE 123"
        
        category = await receipt_parser._auto_categorize(parsed_data, ocr_text)
        
        assert category.value == "transport"
    
    def test_calculate_confidence(self):
        """Test confidence calculation."""
        # High confidence data
        good_data = {
            "amount": 87.50,
            "merchant": "Hotel Berlin",
            "date": "2024-01-15",
            "vat": 14.01
        }
        ocr_text = "HOTEL BERLIN Rechnung 87,50 € MwSt 19%"
        
        confidence = receipt_parser._calculate_confidence(good_data, ocr_text)
        assert confidence >= 80.0
        
        # Low confidence data
        poor_data = {}
        poor_ocr = "unclear text"
        
        confidence = receipt_parser._calculate_confidence(poor_data, poor_ocr)
        assert confidence < 50.0


if __name__ == "__main__":
    # Run a simple test
    async def main():
        parser = receipt_parser
        
        # Test parsing
        ocr_text = """
        HOTEL BERLIN
        Rechnung Nr: 2024-001234
        Datum: 15.01.2024
        Gesamt 87,50 €
        MwSt. 19% 14,01 €
        """
        
        parsed = await parser._parse_text_to_fields(ocr_text)
        print("Parsed data:", parsed)
        
        category = await parser._auto_categorize(parsed, ocr_text)
        print("Category:", category)
        
        confidence = parser._calculate_confidence(parsed, ocr_text)
        print("Confidence:", confidence)
    
    asyncio.run(main())
