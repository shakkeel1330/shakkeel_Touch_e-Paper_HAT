#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont

# Add the library path (adjust if your path is different)
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

# Try to import the e-paper library
try:
    from waveshare_epd import epd2in13_V3  # Use V3 for newer versions
    from waveshare_epd import epdconfig
except ImportError:
    print("E-paper library not found. Make sure you've installed the Waveshare library.")
    print("Download from: https://github.com/waveshare/e-Paper")
    sys.exit(1)

def display_text():
    try:
        print("Initializing e-Paper display...")
        
        # Initialize the display
        epd = epd2in13_V3.EPD()
        epd.init(epd.FULL_UPDATE)
        epd.Clear(0xFF)  # Clear to white
        
        # Create a new image with white background
        # Display dimensions: 250x122 pixels
        image = Image.new('1', (epd.width, epd.height), 255)  # 255 = white
        draw = ImageDraw.Draw(image)
        
        # Try to use a built-in font, fallback to default if not available
        try:
            # Try to load a TrueType font (adjust path as needed)
            font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
        except:
            # Fallback to default font if TrueType font not found
            print("Using default font (TrueType font not found)")
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Your text
        main_text = "I am hungry!!!"
        signature = "- Paathu"
        
        # Get text dimensions for centering
        bbox1 = draw.textbbox((0, 0), main_text, font=font_large)
        text1_width = bbox1[2] - bbox1[0]
        text1_height = bbox1[3] - bbox1[1]
        
        bbox2 = draw.textbbox((0, 0), signature, font=font_small)
        text2_width = bbox2[2] - bbox2[0]
        
        # Calculate positions (centered)
        x1 = (epd.width - text1_width) // 2
        y1 = (epd.height - text1_height) // 2 - 10
        
        x2 = (epd.width - text2_width) // 2
        y2 = y1 + text1_height + 10
        
        # Draw the text (0 = black)
        draw.text((x1, y1), main_text, font=font_large, fill=0)
        draw.text((x2, y2), signature, font=font_small, fill=0)
        
        # Optional: Add a decorative border
        draw.rectangle([(5, 5), (epd.width-5, epd.height-5)], outline=0, width=2)
        
        print("Displaying text on e-Paper...")
        
        # Display the image
        epd.display(epd.getbuffer(image))
        
        print("Text displayed successfully!")
        print("The message will remain on the screen even after the program ends.")
        
        # Put display to sleep to save power
        epd.sleep()
        
    except IOError as e:
        print(f"Error: {e}")
        print("Make sure:")
        print("1. SPI is enabled (sudo raspi-config)")
        print("2. Display is properly connected")
        print("3. You're running with sudo privileges")
        
    except KeyboardInterrupt:
        print("Interrupted by user")
        epdconfig.module_exit()
        exit()

if __name__ == '__main__':
    print("Waveshare 2.13\" E-Paper Text Display")
    print("Displaying: 'I am hungry!!! - Paathu'")
    print("-" * 40)
    
    display_text()
    
    print("\nDone! The text should now be visible on your e-paper display.")
    print("The display will retain this image even when powered off.")
