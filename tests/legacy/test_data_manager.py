"""
Test data management for downloading and caching real receipt images and PDFs.
"""
import os
import requests
from pathlib import Path
from typing import List, Dict
import hashlib


class TestDataManager:
    """Manages downloading and caching of test images and PDFs."""
    
    def __init__(self, cache_dir: str = "tests/test_data"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Real receipt images and PDFs from public sources
        self.test_files = {
            "receipt_image_1": {
                "url": "https://via.placeholder.com/400x600/ffffff/000000.jpg?text=RECEIPT%0A%0ATest+Restaurant%0A123+Main+St%0A%0ADate:+2025-01-15%0ATime:+12:30%0A%0A1x+Coffee++3.50%0A1x+Sandwich++7.50%0A%0ATotal:++11.00%0A%0AThank+you!",
                "filename": "receipt_1.jpg",
                "type": "image",
                "description": "Generated receipt image 1"
            },
            "receipt_image_2": {
                "url": "https://via.placeholder.com/350x500/f8f8f8/333333.jpg?text=GROCERY+RECEIPT%0A%0ASupermarket+ABC%0A456+Oak+Ave%0A%0ADate:+2025-01-14%0A%0AMilk++2.99%0ABread++1.49%0AApples++3.25%0A%0ASubtotal:++7.73%0ATax:++0.62%0ATotal:++8.35%0A%0ACard+Payment",
                "filename": "receipt_2.jpg",
                "type": "image",
                "description": "Generated grocery receipt"
            },
            "receipt_image_3": {
                "url": "https://via.placeholder.com/300x400/ffffff/000000.jpg?text=TAXI+RECEIPT%0A%0ACity+Cab+Co%0ALicense:+TX123%0A%0AFrom:+Airport%0ATo:+Hotel+Downtown%0A%0ADistance:+12.5km%0ATime:+25min%0AFare:+18.50+EUR%0ATip:+2.00+EUR%0ATotal:+20.50+EUR%0A%0APayment:+Credit+Card",
                "filename": "receipt_3.jpg",
                "type": "image",
                "description": "Generated taxi receipt"
            },
            "receipt_pdf_simple": {
                "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                "filename": "simple_receipt.pdf", 
                "type": "pdf",
                "description": "Simple PDF for testing"
            },
            "hotel_receipt": {
                "url": "https://via.placeholder.com/400x550/ffffff/000000.jpg?text=HOTEL+RECEIPT%0A%0AGrand+Hotel+Berlin%0AKurfuerstendamm+123%0A10719+Berlin%0A%0AGuest:+Max+Mustermann%0ARoom:+205%0ACheck-in:+2025-01-10%0ACheck-out:+2025-01-12%0A%0ARoom+(2+nights)++180.00%0ABreakfast+(2x)++30.00%0ACity+tax++6.00%0A%0ASubtotal:++216.00%0AVAT+(19%25):++41.04%0ATotal:++257.04+EUR%0A%0APaid+by+credit+card",
                "filename": "hotel_receipt.jpg",
                "type": "image",
                "description": "Generated hotel receipt"
            },
            "fuel_receipt": {
                "url": "https://via.placeholder.com/320x480/ffffff/000000.jpg?text=FUEL+RECEIPT%0A%0AShell+Station%0AAutobahn+A1+Exit+15%0A%0ADate:+2025-01-13%0ATime:+14:25%0A%0APump:+3%0AFuel:+Super+95%0APrice/L:+1.459+EUR%0ALiters:+45.23%0A%0AAmount:+65.98+EUR%0A%0APayment:+EC+Card%0A%0AMileage:+52,847+km",
                "filename": "fuel_receipt.jpg",
                "type": "image",
                "description": "Generated fuel receipt"
            },
            "parking_receipt": {
                "url": "https://via.placeholder.com/280x350/ffffff/000000.jpg?text=PARKING+RECEIPT%0A%0ACity+Center+Parking%0AMain+Square+Garage%0A%0AEntry:+09:15%0AExit:+17:30%0ADuration:+8h+15m%0A%0ARate:+2.50/hour%0AAmount:+20.00+EUR%0A%0ATicket:+P-789456%0APayment:+Cash",
                "filename": "parking_receipt.jpg",
                "type": "image",
                "description": "Generated parking receipt"
            },
            "flight_receipt": {
                "url": "https://via.placeholder.com/400x300/ffffff/000000.jpg?text=FLIGHT+RECEIPT%0A%0ALufthansa+LH1234%0AFRA+-+BER%0A%0APassenger:+M.+Mustermann%0ASeat:+12A%0AClass:+Economy%0A%0ADate:+2025-01-15%0ADeparture:+08:30%0AArrival:+09:45%0A%0ATicket+Price:+89.99+EUR%0ATaxes:+45.21+EUR%0ATotal:+135.20+EUR",
                "filename": "flight_receipt.jpg",
                "type": "image",
                "description": "Generated flight receipt"
            }
        }
    
    def download_file(self, key: str, force_download: bool = False) -> Path:
        """Download a test file if not cached."""
        if key not in self.test_files:
            raise ValueError(f"Unknown test file key: {key}")
        
        file_info = self.test_files[key]
        file_path = self.cache_dir / file_info["filename"]
        
        # Return cached file if exists and not forcing download
        if file_path.exists() and not force_download:
            return file_path
        
        try:
            print(f"Downloading {file_info['description']}: {file_info['url']}")
            response = requests.get(file_info["url"], timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {file_path}")
            return file_path
            
        except requests.RequestException as e:
            print(f"Failed to download {key}: {e}")
            # Create a dummy file for testing if download fails
            return self._create_dummy_file(file_info)
    
    def _create_dummy_file(self, file_info: Dict) -> Path:
        """Create a dummy file when download fails."""
        file_path = self.cache_dir / f"dummy_{file_info['filename']}"
        
        if file_info["type"] == "image":
            # Create a realistic receipt image
            try:
                from PIL import Image, ImageDraw, ImageFont
                
                # Create white background
                img = Image.new('RGB', (400, 600), color='white')
                draw = ImageDraw.Draw(img)
                
                # Try to use a monospace font for better receipt appearance
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Courier.ttc", 16)
                    small_font = ImageFont.truetype("/System/Library/Fonts/Courier.ttc", 14)
                except:
                    font = ImageFont.load_default()
                    small_font = ImageFont.load_default()
                
                # Generate different receipt types based on filename
                if "hotel" in file_info['filename'].lower():
                    lines = [
                        "GRAND HOTEL BERLIN",
                        "Kurfuerstendamm 123",
                        "10719 Berlin, Germany",
                        "Tel: +49 30 12345678",
                        "",
                        "GUEST RECEIPT",
                        "=" * 25,
                        "Guest: Max Mustermann", 
                        "Room: 205 (Superior)",
                        "Check-in: 2025-01-10 15:00",
                        "Check-out: 2025-01-12 11:00",
                        "",
                        "CHARGES:",
                        "Room (2 nights)    €180.00",
                        "Breakfast (2x)      €30.00", 
                        "City Tax             €6.00",
                        "WiFi                 €0.00",
                        "",
                        "Subtotal:          €216.00",
                        "VAT (19%):          €41.04",
                        "TOTAL:             €257.04",
                        "",
                        "Payment: Credit Card",
                        "Card: ****1234",
                        "",
                        "Thank you for staying!"
                    ]
                elif "fuel" in file_info['filename'].lower() or "gas" in file_info['filename'].lower():
                    lines = [
                        "SHELL STATION",
                        "Autobahn A1 Exit 15",
                        "12345 Fuel City",
                        "",
                        "FUEL RECEIPT",
                        "=" * 20,
                        "Date: 2025-01-13",
                        "Time: 14:25:33",
                        "",
                        "Pump: 3",
                        "Product: Super 95",
                        "Price/L: €1.459",
                        "Liters: 45.23",
                        "",
                        "Amount: €65.98",
                        "",
                        "Payment: EC Card",
                        "Card: ****5678",
                        "",
                        "Mileage: 52,847 km",
                        "",
                        "Thank you!"
                    ]
                elif "taxi" in file_info['filename'].lower():
                    lines = [
                        "CITY CAB COMPANY",
                        "License: TX-123456",
                        "Driver: Hans Mueller",
                        "Tel: +49 30 987654321",
                        "",
                        "TAXI RECEIPT",
                        "=" * 20,
                        "Date: 2025-01-14",
                        "Time: 16:45 - 17:10",
                        "",
                        "From: Airport Terminal 1",
                        "To: Hotel Downtown",
                        "",
                        "Distance: 12.5 km",
                        "Duration: 25 minutes",
                        "",
                        "Base Fare:     €4.50",
                        "Distance:     €12.50",
                        "Time:          €1.50",
                        "Tip:           €2.00",
                        "",
                        "TOTAL:        €20.50",
                        "",
                        "Payment: Credit Card"
                    ]
                elif "parking" in file_info['filename'].lower():
                    lines = [
                        "CITY CENTER PARKING",
                        "Main Square Garage",
                        "Level B2, Space 247",
                        "",
                        "PARKING RECEIPT",
                        "=" * 20,
                        "Ticket: P-789456123",
                        "",
                        "Entry:  09:15:22",
                        "Exit:   17:30:45",
                        "Duration: 8h 15m",
                        "",
                        "Rate: €2.50/hour",
                        "Amount: €20.00",
                        "",
                        "Payment: Cash",
                        "",
                        "Thank you!"
                    ]
                elif "flight" in file_info['filename'].lower():
                    lines = [
                        "LUFTHANSA",
                        "Flight LH1234",
                        "FRA → BER",
                        "",
                        "E-TICKET RECEIPT",
                        "=" * 20,
                        "Passenger:",
                        "MUSTERMANN/MAX MR",
                        "",
                        "Date: 15JAN25",
                        "Departure: 08:30",
                        "Arrival: 09:45",
                        "Seat: 12A",
                        "Class: Economy",
                        "",
                        "Ticket Price: €89.99",
                        "Taxes & Fees: €45.21",
                        "TOTAL: €135.20",
                        "",
                        "PNR: ABC123",
                        "Ticket: 220-1234567890"
                    ]
                else:
                    # Default restaurant receipt
                    lines = [
                        "CAFE BISTRO BERLIN",
                        "Unter den Linden 123", 
                        "10117 Berlin",
                        "Tel: +49 30 12345678",
                        "",
                        "RECEIPT / RECHNUNG",
                        "=" * 25,
                        "Date: 2025-01-15",
                        "Time: 12:30:45",
                        "Table: 7",
                        "Guests: 2",
                        "",
                        "1x Espresso          €2.50",
                        "1x Cappuccino        €3.20",
                        "1x Club Sandwich     €8.50",
                        "1x Caesar Salad      €7.80",
                        "2x Mineral Water     €5.00",
                        "",
                        "Subtotal:          €27.00",
                        "VAT (19%):          €5.13",
                        "TOTAL:             €32.13",
                        "",
                        "Payment: Credit Card",
                        "Card: ****1234",
                        "",
                        "Vielen Dank!",
                        "Thank you!"
                    ]
                
                # Draw the receipt content
                y = 20
                for line in lines:
                    if line.startswith("="):
                        # Draw separator line
                        draw.line([(30, y+8), (370, y+8)], fill='black', width=1)
                        y += 20
                    elif line == "":
                        y += 15
                    else:
                        # Use different fonts for headers vs content
                        current_font = font if any(header in line.upper() for header in ["RECEIPT", "HOTEL", "CAFE", "SHELL", "TAXI", "PARKING", "LUFTHANSA", "TOTAL:"]) else small_font
                        draw.text((30, y), line, fill='black', font=current_font)
                        y += 20
                
                # Add a border
                draw.rectangle([(10, 10), (390, 590)], outline='black', width=2)
                
                img.save(file_path, 'JPEG', quality=95)
                
            except ImportError:
                # Fallback: create a simple text file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Dummy receipt image for testing: {file_info['description']}\n")
                    f.write("CAFE BISTRO\n")
                    f.write("Receipt #12345\n") 
                    f.write("Date: 2025-01-15\n")
                    f.write("Total: €25.50\n")
        
        elif file_info["type"] == "pdf":
            # Create a simple PDF-like file with receipt content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("%PDF-1.4\n")
                f.write("% Dummy PDF receipt for testing\n")
                f.write("1 0 obj\n")
                f.write("<<\n")
                f.write("/Type /Catalog\n") 
                f.write("/Pages 2 0 R\n")
                f.write(">>\n")
                f.write("endobj\n")
                f.write("\n")
                f.write("2 0 obj\n")
                f.write("<<\n")
                f.write("/Type /Pages\n")
                f.write("/Kids [3 0 R]\n")
                f.write("/Count 1\n")
                f.write(">>\n")
                f.write("endobj\n")
                f.write("\n")
                f.write("3 0 obj\n")
                f.write("<<\n")
                f.write("/Type /Page\n")
                f.write("/Parent 2 0 R\n")
                f.write("/MediaBox [0 0 612 792]\n")
                f.write(">>\n")
                f.write("endobj\n")
                f.write("\n")
                f.write("xref\n")
                f.write("0 4\n")
                f.write("0000000000 65535 f \n")
                f.write("0000000009 65535 n \n")
                f.write("0000000074 65535 n \n")
                f.write("0000000131 65535 n \n")
                f.write("trailer\n")
                f.write("<<\n")
                f.write("/Size 4\n")
                f.write("/Root 1 0 R\n")
                f.write(">>\n")
                f.write("startxref\n")
                f.write("0\n")
                f.write("%%EOF\n")
        
        return file_path
    
    def get_all_files(self) -> Dict[str, Path]:
        """Download all test files and return their paths."""
        files = {}
        for key in self.test_files:
            try:
                files[key] = self.download_file(key)
            except Exception as e:
                print(f"Error getting file {key}: {e}")
        return files
    
    def generate_synthetic_receipts(self) -> Dict[str, Path]:
        """Generate synthetic receipt images locally for testing."""
        synthetic_receipts = {
            "synthetic_restaurant": {
                "filename": "synthetic_restaurant.jpg",
                "type": "image",
                "description": "Synthetic restaurant receipt"
            },
            "synthetic_hotel": {
                "filename": "synthetic_hotel.jpg", 
                "type": "image",
                "description": "Synthetic hotel receipt"
            },
            "synthetic_taxi": {
                "filename": "synthetic_taxi.jpg",
                "type": "image", 
                "description": "Synthetic taxi receipt"
            },
            "synthetic_fuel": {
                "filename": "synthetic_fuel.jpg",
                "type": "image",
                "description": "Synthetic fuel receipt"
            },
            "synthetic_parking": {
                "filename": "synthetic_parking.jpg",
                "type": "image",
                "description": "Synthetic parking receipt"
            },
            "synthetic_flight": {
                "filename": "synthetic_flight.jpg",
                "type": "image",
                "description": "Synthetic flight receipt"
            }
        }
        
        generated_files = {}
        for key, info in synthetic_receipts.items():
            file_path = self._create_dummy_file(info)
            generated_files[key] = file_path
            print(f"Generated synthetic receipt: {file_path}")
        
        return generated_files
    
    def cleanup(self):
        """Remove all cached test files."""
        for file_path in self.cache_dir.glob("*"):
            if file_path.is_file():
                file_path.unlink()
        print(f"Cleaned up test data in {self.cache_dir}")


# Global instance for easy access
test_data_manager = TestDataManager()
