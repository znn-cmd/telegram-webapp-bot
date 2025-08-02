#!/usr/bin/env python3
"""
Simple PDF generation test
"""

import os
import sys
from datetime import datetime

# Set environment variables
os.environ['SUPABASE_URL'] = "https://dzllnnohurlzjyabgsft.supabase.co"
os.environ['SUPABASE_KEY'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6bGxubm9odXJsemp5YWJnc2Z0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA5NDgwMjcsImV4cCI6MjA2NjUyNDAyN30.sJCIeeIm0Ye1JbAdw5HzfAMe8QLgQomArK8yoppuevQ"

def test_simple_pdf():
    """Test simple PDF creation"""
    print("🧪 Testing Simple PDF Creation")
    print("=" * 40)
    
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        
        # Create a simple PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add font
        pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf')
        pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf')
        
        # Add content
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, 'Test PDF', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 8, f'Generated at: {datetime.now()}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Save PDF
        pdf.output('test_simple.pdf')
        print("✅ Simple PDF created successfully")
        
    except Exception as e:
        print(f"❌ Error creating simple PDF: {e}")
        import traceback
        traceback.print_exc()

def test_pdf_with_charts():
    """Test PDF creation with charts"""
    print("\n🧪 Testing PDF with Charts")
    print("=" * 40)
    
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        from app import create_property_trends_chart
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add font
        pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf')
        pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf')
        
        # Add content
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, 'Test PDF with Charts', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        # Test data
        historical_data = {
            'years': [2021, 2022, 2023, 2024, 2025],
            'sale_prices': [1000, 1100, 1200, 1300, 1400],
            'rent_prices': [10, 11, 12, 13, 14]
        }
        
        # Create and add chart
        chart_buffer = create_property_trends_chart(historical_data, 'sale', 180, 80)
        if chart_buffer:
            pdf.ln(10)
            pdf.image(chart_buffer, x=15, w=180)
            print("✅ Chart added to PDF successfully")
        else:
            print("❌ Failed to create chart")
        
        # Save PDF
        pdf.output('test_with_charts.pdf')
        print("✅ PDF with charts created successfully")
        
    except Exception as e:
        print(f"❌ Error creating PDF with charts: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_pdf()
    test_pdf_with_charts() 