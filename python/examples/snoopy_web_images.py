#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Snoopy Web Images for Waveshare 2.13" V4 Touch e-Paper Display
Created for Raspberry Pi Zero 2W

This program downloads Snoopy images from the web and displays them on the e-paper display:
- Downloads Snoopy images and comic strips from various sources
- Resizes images to fit the 250x122 display resolution
- Cycles through different images with touch interaction
- Handles image processing for optimal e-paper display
"""

import sys
import os
import time
import logging
import threading
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
import traceback
from io import BytesIO

# Set up paths
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic/2in13')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

from TP_lib import gt1151
from TP_lib import epd2in13_V4

logging.basicConfig(level=logging.DEBUG)

# Collection of Snoopy images from various sources
SNOOPY_IMAGES = [
    # Simple Snoopy images (these are placeholder URLs - you'll need to replace with actual working URLs)
    {
        'name': 'Snoopy Happy',
        'url': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Snoopy_Peanuts.png/220px-Snoopy_Peanuts.png',
        'description': 'Classic Snoopy'
    },
    {
        'name': 'Snoopy Dancing',
        'url': 'https://www.pngitem.com/pimgs/m/184-1842507_snoopy-dancing-png-transparent-png.png',
        'description': 'Dancing Snoopy'
    },
    {
        'name': 'Snoopy Sleeping',
        'url': 'https://www.pngitem.com/pimgs/m/184-1842508_snoopy-sleeping-png-transparent-png.png',
        'description': 'Sleeping Snoopy'
    },
    {
        'name': 'Snoopy Flying Ace',
        'url': 'https://www.pngitem.com/pimgs/m/184-1842509_snoopy-flying-ace-png-transparent-png.png',
        'description': 'Flying Ace Snoopy'
    }
]

# Alternative: Use local placeholder images if web images fail
LOCAL_IMAGES = [
    'Menu.bmp',
    'Photo_1.bmp',
    'Photo_2.bmp'
]

class SnoopyWebImages:
    def __init__(self):
        self.epd = epd2in13_V4.EPD()
        self.gt = gt1151.GT1151()
        self.GT_Dev = gt1151.GT_Development()
        self.GT_Old = gt1151.GT_Development()
        
        # Display dimensions for 2.13" V4
        self.width = 122
        self.height = 250
        
        # Image management
        self.current_image_index = 0
        self.images = []
        self.image_cache = {}
        
        # Threading
        self.flag_t = 1
        self.touch_thread = None
        
    def init_display(self):
        """Initialize the e-paper display and touch controller"""
        logging.info("Initializing Snoopy Web Images Display")
        
        # Initialize display
        self.epd.init(self.epd.FULL_UPDATE)
        self.gt.GT_Init()
        self.epd.Clear(0xFF)  # Clear with white background
        
        # Start touch detection thread
        self.touch_thread = threading.Thread(target=self.touch_irq_handler)
        self.touch_thread.setDaemon(True)
        self.touch_thread.start()
        
        logging.info("Display initialized successfully")
        
    def touch_irq_handler(self):
        """Handle touch interrupt in separate thread"""
        logging.info("Touch detection thread started")
        while self.flag_t == 1:
            if self.gt.digital_read(self.gt.INT) == 0:
                self.GT_Dev.Touch = 1
            else:
                self.GT_Dev.Touch = 0
        logging.info("Touch detection thread stopped")
        
    def download_image(self, url, timeout=10):
        """Download image from URL"""
        try:
            logging.info(f"Downloading image from: {url}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Open image from bytes
            image = Image.open(BytesIO(response.content))
            logging.info(f"Successfully downloaded image: {image.size}")
            return image
            
        except Exception as e:
            logging.error(f"Failed to download image from {url}: {e}")
            return None
            
    def process_image_for_epaper(self, image):
        """Process image for optimal e-paper display"""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Resize to fit display while maintaining aspect ratio
            display_ratio = self.height / self.width  # 250/122 = 2.05
            
            # Calculate new size
            img_width, img_height = image.size
            img_ratio = img_height / img_width
            
            if img_ratio > display_ratio:
                # Image is taller than display ratio
                new_height = self.height
                new_width = int(self.height / img_ratio)
            else:
                # Image is wider than display ratio
                new_width = self.width
                new_height = int(self.width * img_ratio)
            
            # Resize image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create a white background image of display size
            background = Image.new('L', (self.width, self.height), 255)
            
            # Calculate position to center the image
            x_offset = (self.width - new_width) // 2
            y_offset = (self.height - new_height) // 2
            
            # Paste the resized image onto the background
            background.paste(image, (x_offset, y_offset))
            
            # Convert to 1-bit (black and white) for e-paper
            # Use threshold to create clear black and white image
            threshold = 128
            background = background.point(lambda x: 0 if x < threshold else 255, '1')
            
            logging.info(f"Processed image to display size: {background.size}")
            return background
            
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            return None
            
    def load_local_images(self):
        """Load local images as fallback"""
        logging.info("Loading local images as fallback")
        local_images = []
        
        for img_name in LOCAL_IMAGES:
            img_path = os.path.join(picdir, img_name)
            if os.path.exists(img_path):
                try:
                    image = Image.open(img_path)
                    processed_image = self.process_image_for_epaper(image)
                    if processed_image:
                        local_images.append({
                            'name': img_name,
                            'image': processed_image,
                            'description': f'Local image: {img_name}'
                        })
                        logging.info(f"Loaded local image: {img_name}")
                except Exception as e:
                    logging.error(f"Error loading local image {img_name}: {e}")
                    
        return local_images
        
    def load_web_images(self):
        """Load images from web sources"""
        logging.info("Attempting to load web images")
        web_images = []
        
        for img_info in SNOOPY_IMAGES:
            try:
                # Download image
                image = self.download_image(img_info['url'])
                if image:
                    # Process for e-paper
                    processed_image = self.process_image_for_epaper(image)
                    if processed_image:
                        web_images.append({
                            'name': img_info['name'],
                            'image': processed_image,
                            'description': img_info['description']
                        })
                        logging.info(f"Successfully loaded web image: {img_info['name']}")
                        
            except Exception as e:
                logging.error(f"Error loading web image {img_info['name']}: {e}")
                
        return web_images
        
    def create_text_overlay(self, image_info):
        """Create text overlay for image information"""
        overlay = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(overlay)
        
        try:
            font_small = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 10)
        except:
            font_small = ImageFont.load_default()
            
        # Draw semi-transparent background for text
        text_bg_height = 25
        draw.rectangle([0, 0, self.width, text_bg_height], fill=255, outline=0, width=1)
        
        # Draw image name
        draw.text((5, 5), image_info['name'], font=font_small, fill=0)
        
        # Draw description
        draw.text((5, 18), image_info['description'], font=font_small, fill=0)
        
        return overlay
        
    def display_image(self, image_info):
        """Display image on e-paper display"""
        try:
            # Get the image
            image = image_info['image']
            
            # Create text overlay
            overlay = self.create_text_overlay(image_info)
            
            # Combine image and overlay
            # For e-paper, we want text to be visible, so we'll overlay it
            combined_image = image.copy()
            
            # Paste overlay onto combined image
            # We'll make the text area slightly transparent by inverting some pixels
            for y in range(overlay.height):
                for x in range(overlay.width):
                    if overlay.getpixel((x, y)) == 0:  # Black text
                        # Make the background area slightly darker for better text visibility
                        current_pixel = combined_image.getpixel((x, y))
                        if current_pixel == 255:  # White background
                            combined_image.putpixel((x, y), 200)  # Light gray
                        else:
                            combined_image.putpixel((x, y), 0)  # Black text
            
            # Display the image
            self.epd.display(self.epd.getbuffer(combined_image))
            logging.info(f"Displayed image: {image_info['name']}")
            
        except Exception as e:
            logging.error(f"Error displaying image: {e}")
            
    def handle_touch(self, x, y):
        """Handle touch input to cycle through images"""
        # Simple touch anywhere to cycle to next image
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        logging.info(f"Touch detected - switching to image {self.current_image_index}")
        
        if self.images:
            self.display_image(self.images[self.current_image_index])
            
    def run(self):
        """Main display loop"""
        try:
            self.init_display()
            
            # Try to load web images first
            self.images = self.load_web_images()
            
            # If no web images loaded, fall back to local images
            if not self.images:
                logging.info("No web images loaded, using local images")
                self.images = self.load_local_images()
                
            if not self.images:
                logging.error("No images available to display")
                return
                
            logging.info(f"Loaded {len(self.images)} images")
            
            # Display first image
            self.display_image(self.images[0])
            
            # Main loop for touch detection
            while True:
                # Check for touch input
                self.gt.GT_Scan(self.GT_Dev, self.GT_Old)
                
                # Detect new touch
                if (self.GT_Old.X[0] != self.GT_Dev.X[0] or 
                    self.GT_Old.Y[0] != self.GT_Dev.Y[0] or 
                    self.GT_Old.S[0] != self.GT_Dev.S[0]):
                    
                    if self.GT_Dev.TouchpointFlag:
                        # Handle touch
                        touch_x = self.GT_Dev.X[0]
                        touch_y = self.GT_Dev.Y[0]
                        
                        # Only process if touch is within display bounds
                        if 0 <= touch_x < self.width and 0 <= touch_y < self.height:
                            self.handle_touch(touch_x, touch_y)
                            
                        self.GT_Dev.TouchpointFlag = 0
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logging.info("Display interrupted by user")
            
        except Exception as e:
            logging.error(f"Display error: {e}")
            traceback.print_exc()
            
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        logging.info("Cleaning up...")
        self.flag_t = 0
        
        if self.touch_thread and self.touch_thread.is_alive():
            self.touch_thread.join(timeout=1)
            
        try:
            self.epd.sleep()
            self.epd.Dev_exit()
        except:
            pass
            
        logging.info("Cleanup complete")

def main():
    """Main function"""
    logging.info("Starting Snoopy Web Images Display")
    
    try:
        display = SnoopyWebImages()
        display.run()
        
    except Exception as e:
        logging.error(f"Main error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 