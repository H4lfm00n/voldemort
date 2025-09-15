#!/usr/bin/env python3
"""
QR Code Generator for SFSU Classroom Links
Generates QR codes for each classroom link and saves them with room number filenames
"""

import json
import os
import qrcode
from PIL import Image
from typing import List, Dict
from loguru import logger


class ClassroomQRGenerator:
    def __init__(self, json_file: str = "sfsu_classrooms.json", output_dir: str = "qr_codes"):
        self.json_file = json_file
        self.output_dir = output_dir
        self.qr_codes_generated = 0
        
    def load_classroom_data(self) -> List[Dict[str, str]]:
        """Load classroom data from JSON file."""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            rooms = data.get('rooms', [])
            logger.info(f"Loaded {len(rooms)} rooms from {self.json_file}")
            return rooms
        except FileNotFoundError:
            logger.error(f"JSON file not found: {self.json_file}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.json_file}: {e}")
            return []
    
    def create_output_directory(self):
        """Create output directory for QR codes."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
        else:
            logger.info(f"Using existing output directory: {self.output_dir}")
    
    def sanitize_filename(self, room_number: str) -> str:
        """Sanitize room number for use as filename."""
        # Replace spaces and special characters with underscores
        sanitized = room_number.replace(' ', '_').replace('/', '_').replace('\\', '_')
        # Remove any other potentially problematic characters
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '_-')
        return sanitized
    
    def generate_qr_code(self, room_number: str, link: str) -> bool:
        """Generate QR code for a single classroom link."""
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,  # Controls the size of the QR Code
                error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
                box_size=10,  # Size of each box in pixels
                border=4,  # Border size in boxes
            )
            
            # Add data to QR code
            qr.add_data(link)
            qr.make(fit=True)
            
            # Create image from QR code
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Sanitize room number for filename
            filename = self.sanitize_filename(room_number)
            filepath = os.path.join(self.output_dir, f"{filename}.png")
            
            # Save QR code image
            img.save(filepath)
            logger.debug(f"Generated QR code for {room_number}: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating QR code for {room_number}: {e}")
            return False
    
    def generate_all_qr_codes(self) -> Dict[str, int]:
        """Generate QR codes for all classrooms."""
        # Load classroom data
        rooms = self.load_classroom_data()
        if not rooms:
            logger.error("No classroom data loaded")
            return {"success": 0, "failed": 0, "total": 0}
        
        # Create output directory
        self.create_output_directory()
        
        # Generate QR codes
        success_count = 0
        failed_count = 0
        
        logger.info(f"Starting QR code generation for {len(rooms)} rooms...")
        
        for i, room in enumerate(rooms, 1):
            room_number = room.get('room_number', '')
            link = room.get('link', '')
            
            if not room_number or not link:
                logger.warning(f"Skipping room {i}: missing room_number or link")
                failed_count += 1
                continue
            
            logger.info(f"Generating QR code {i}/{len(rooms)}: {room_number}")
            
            if self.generate_qr_code(room_number, link):
                success_count += 1
            else:
                failed_count += 1
        
        self.qr_codes_generated = success_count
        
        result = {
            "success": success_count,
            "failed": failed_count,
            "total": len(rooms)
        }
        
        logger.info(f"QR code generation completed: {success_count} successful, {failed_count} failed")
        return result
    
    def generate_batch_qr_codes(self, room_numbers: List[str] = None) -> Dict[str, int]:
        """Generate QR codes for specific rooms only."""
        # Load classroom data
        rooms = self.load_classroom_data()
        if not rooms:
            logger.error("No classroom data loaded")
            return {"success": 0, "failed": 0, "total": 0}
        
        # Filter rooms if specific room numbers provided
        if room_numbers:
            rooms = [room for room in rooms if room.get('room_number') in room_numbers]
            logger.info(f"Filtered to {len(rooms)} specific rooms")
        
        # Create output directory
        self.create_output_directory()
        
        # Generate QR codes
        success_count = 0
        failed_count = 0
        
        logger.info(f"Starting batch QR code generation for {len(rooms)} rooms...")
        
        for i, room in enumerate(rooms, 1):
            room_number = room.get('room_number', '')
            link = room.get('link', '')
            
            if not room_number or not link:
                logger.warning(f"Skipping room {i}: missing room_number or link")
                failed_count += 1
                continue
            
            logger.info(f"Generating QR code {i}/{len(rooms)}: {room_number}")
            
            if self.generate_qr_code(room_number, link):
                success_count += 1
            else:
                failed_count += 1
        
        result = {
            "success": success_count,
            "failed": failed_count,
            "total": len(rooms)
        }
        
        logger.info(f"Batch QR code generation completed: {success_count} successful, {failed_count} failed")
        return result
    
    def list_generated_qr_codes(self) -> List[str]:
        """List all generated QR code files."""
        if not os.path.exists(self.output_dir):
            return []
        
        qr_files = []
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.png'):
                qr_files.append(filename)
        
        return sorted(qr_files)
    
    def cleanup_qr_codes(self):
        """Remove all generated QR code files."""
        if not os.path.exists(self.output_dir):
            logger.info("No QR codes directory to clean up")
            return
        
        qr_files = self.list_generated_qr_codes()
        for filename in qr_files:
            filepath = os.path.join(self.output_dir, filename)
            try:
                os.remove(filepath)
                logger.debug(f"Removed: {filepath}")
            except Exception as e:
                logger.error(f"Error removing {filepath}: {e}")
        
        logger.info(f"Cleaned up {len(qr_files)} QR code files")


def main():
    """Main function to run the QR code generator."""
    generator = ClassroomQRGenerator()
    
    # Generate QR codes for all rooms
    result = generator.generate_all_qr_codes()
    
    if result["success"] > 0:
        print(f"\nQR Code Generation Completed!")
        print(f"✅ Successfully generated: {result['success']} QR codes")
        print(f"❌ Failed: {result['failed']} QR codes")
        print(f"📁 Output directory: {generator.output_dir}")
        
        # Show sample of generated files
        qr_files = generator.list_generated_qr_codes()
        if qr_files:
            print(f"\nSample generated files:")
            for filename in qr_files[:10]:  # Show first 10
                print(f"  📱 {filename}")
            if len(qr_files) > 10:
                print(f"  ... and {len(qr_files) - 10} more")
    else:
        print("❌ QR code generation failed - no codes were generated")


if __name__ == "__main__":
    main()
