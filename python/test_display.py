#!/usr/bin/env python3
"""
Simple test script to verify the e-Paper display is working
"""

import sys
import os
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Add the lib directory to Python path
current_dir = os.path.dirname(os.path.realpath(__file__))
lib_dir = os.path.join(current_dir, 'lib')
sys.path.insert(0, lib_dir)

try:
    # Import the display driver
    from TP_lib import epd2in9_V2
    epd = epd2in9_V2.EPD_2IN9_V2()
    
    print("Display driver imported successfully!")
    
    # Initialize display
    print("Initializing display...")
    epd.init()
    epd.Clear()
    print("Display cleared successfully!")
    
    # Create a simple test image
    print("Creating test image...")
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    
    # Draw some test text
    draw.rectangle((0, 0, 295, 40), fill='black')
    draw.text((10, 10), 'DISPLAY TEST', fill='white')
    draw.text((10, 60), f'Time: {datetime.now().strftime("%H:%M:%S")}', fill='black')
    draw.text((10, 90), 'If you can see this,', fill='black')
    draw.text((10, 120), 'the display is working!', fill='black')
    draw.text((10, 150), 'Press Ctrl+C to exit', fill='black')
    
    # Display the image
    print("Displaying test image...")
    epd.display(epd.getbuffer(image))
    print("Test image displayed successfully!")
    
    print("\nDisplay test completed successfully!")
    print("If you can see the test image on your e-Paper display, everything is working.")
    print("You can now run the real-time display with: sudo python3 standalone_realtime.py")
    
except ImportError as e:
    print(f"Import Error: {e}")
    print("Make sure you're running this from the python directory")
    print("and the TP_lib module is available")
except Exception as e:
    print(f"Error: {e}")
    print("Make sure the e-Paper display is properly connected")
    import traceback
    traceback.print_exc()
finally:
    try:
        epd.module_exit()
    except:
        pass 