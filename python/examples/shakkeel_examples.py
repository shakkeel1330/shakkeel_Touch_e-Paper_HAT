#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

# Set up paths (adjust these if your directory structure is different)
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic/2in13')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

from TP_lib import epd2in13_V4
import time
import logging
from PIL import Image, ImageDraw, ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("Starting simple quote display")
    
    # Initialize the e-paper display
    epd = epd2in13_V4.EPD()
    logging.info("Initializing display...")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)  # Clear with white background
    
    # Create a new image with white background
    # The display is 122x250 pixels
    image = Image.new('1', (epd.height, epd.width), 255)  # 255 = white background
    draw = ImageDraw.Draw(image)
    
    # Load fonts - try different sizes
    try:
        font_large = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 20)
        font_small = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 16)
    except:
        # Fallback to default font if custom font not found
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # The quote text
    quote_text = "I am hungry!!!"
    author_text = "* Paathu"
    
    # Get text dimensions for centering
    quote_bbox = draw.textbbox((0, 0), quote_text, font=font_large)
    author_bbox = draw.textbbox((0, 0), author_text, font=font_small)
    
    quote_width = quote_bbox[2] - quote_bbox[0]
    quote_height = quote_bbox[3] - quote_bbox[1]
    author_width = author_bbox[2] - author_bbox[0]
    author_height = author_bbox[3] - author_bbox[1]
    
    # Calculate positions for centering
    display_width = epd.height  # 122
    display_height = epd.width  # 250
    
    quote_x = (display_width - quote_width) // 2
    quote_y = (display_height - quote_height - author_height - 20) // 2  # 20px spacing
    
    author_x = (display_width - author_width) // 2
    author_y = quote_y + quote_height + 20
    
    # Draw the text
    draw.text((quote_x, quote_y), quote_text, font=font_large, fill=0)  # 0 = black
    draw.text((author_x, author_y), author_text, font=font_small, fill=0)
    
    # Display the image
    logging.info("Displaying quote...")
    epd.display(epd.getbuffer(image))
    
    logging.info("Quote displayed successfully!")
    logging.info("The display will remain showing the quote until you run another script or power off.")
    
    # Put the display to sleep to save power
    time.sleep(2)
    epd.sleep()
    
except IOError as e:
    logging.error(f"IO Error: {e}")
    
except KeyboardInterrupt:    
    logging.info("Interrupted by user")
    epd.sleep()
    
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    traceback.print_exc()
    
finally:
    # Clean up
    try:
        epd.Dev_exit()
    except:
        pass
