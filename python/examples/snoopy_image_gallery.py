#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Snoopy Image Gallery for Waveshare 2.13" V4 Touch e-Paper Display
Created for Raspberry Pi Zero 2W

This program displays Snoopy images and creates custom Snoopy drawings:
- Uses working Snoopy images from reliable sources
- Creates custom Snoopy drawings programmatically
- Resizes images to fit the 250x122 display resolution
- Cycles through different images with touch interaction
"""

import sys
import os
import time
import logging
import threading
import requests
from PIL import Image, ImageDraw, ImageFont
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

# Working Snoopy images from reliable sources
WORKING_SNOOPY_IMAGES = [
    {
        'name': 'Snoopy Classic',
        'url': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Snoopy_Peanuts.png/220px-Snoopy_Peanuts.png',
        'description': 'Classic Snoopy'
    },
    {
        'name': 'Snoopy Wiki',
        'url': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Snoopy_Peanuts.png/150px-Snoopy_Peanuts.png',
        'description': 'Snoopy from Wikipedia'
    }
]

class SnoopyImageGallery:
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
        
        # Threading
        self.flag_t = 1
        self.touch_thread = None
        
    def init_display(self):
        """Initialize the e-paper display and touch controller"""
        logging.info("Initializing Snoopy Image Gallery")
        
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
        
    def download_image(self, url, timeout=15):
        """Download image from URL"""
        try:
            logging.info(f"Downloading image from: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, timeout=timeout, headers=headers)
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
            
    def create_snoopy_drawing(self, pose='classic'):
        """Create a custom Snoopy drawing"""
        # Create a new image
        image = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)
        
        # Center position
        center_x = self.width // 2
        center_y = self.height // 2
        
        if pose == 'classic':
            # Draw classic Snoopy
            self.draw_classic_snoopy(draw, center_x, center_y)
        elif pose == 'dancing':
            # Draw dancing Snoopy
            self.draw_dancing_snoopy(draw, center_x, center_y)
        elif pose == 'sleeping':
            # Draw sleeping Snoopy
            self.draw_sleeping_snoopy(draw, center_x, center_y)
        elif pose == 'happy':
            # Draw happy Snoopy
            self.draw_happy_snoopy(draw, center_x, center_y)
            
        return image
        
    def draw_classic_snoopy(self, draw, x, y):
        """Draw classic Snoopy pose"""
        # Head (white oval)
        head_width = 20
        head_height = 18
        draw.ellipse([x - head_width//2, y - head_height//2, 
                     x + head_width//2, y + head_height//2], 
                    fill=255, outline=0, width=2)
        
        # Long black nose
        nose_length = 10
        nose_width = 4
        nose_x = x + head_width//2 - 3
        nose_y = y + 1
        draw.ellipse([nose_x, nose_y, nose_x + nose_length, nose_y + nose_width], fill=0)
        
        # Ears
        ear_width = 8
        ear_height = 10
        # Left ear
        draw.ellipse([x - head_width//2 - 4, y - head_height//2 - 3,
                     x - head_width//2 + 4, y - head_height//2 + 7],
                    fill=255, outline=0, width=1)
        # Right ear
        draw.ellipse([x + head_width//2 - 4, y - head_height//2 - 3,
                     x + head_width//2 + 4, y - head_height//2 + 7],
                    fill=255, outline=0, width=1)
        
        # Eyes
        eye_y = y - 2
        draw.ellipse([x - 7, eye_y, x - 3, eye_y + 3], fill=0)
        draw.ellipse([x + 3, eye_y, x + 7, eye_y + 3], fill=0)
        
        # Body
        body_width = 18
        body_height = 25
        draw.ellipse([x - body_width//2, y + 8, 
                     x + body_width//2, y + 8 + body_height], 
                    fill=255, outline=0, width=2)
        
        # Collar
        collar_y = y + 12
        draw.ellipse([x - body_width//2 + 2, collar_y, 
                     x + body_width//2 - 2, collar_y + 5], 
                    fill=0, outline=0, width=1)
        
        # Arms
        arm_y = y + 18
        draw.line([x - body_width//2, arm_y, x - body_width//2 - 6, arm_y + 8], fill=0, width=2)
        draw.line([x + body_width//2, arm_y, x + body_width//2 + 6, arm_y + 8], fill=0, width=2)
        
        # Legs
        leg_y = y + 8 + body_height
        draw.line([x - 5, leg_y, x - 5, leg_y + 12], fill=0, width=3)
        draw.line([x + 5, leg_y, x + 5, leg_y + 12], fill=0, width=3)
        
        # Feet
        draw.ellipse([x - 8, leg_y + 10, x - 2, leg_y + 16], fill=0)
        draw.ellipse([x + 2, leg_y + 10, x + 8, leg_y + 16], fill=0)
        
    def draw_dancing_snoopy(self, draw, x, y):
        """Draw dancing Snoopy"""
        # Similar to classic but with raised arms and movement
        self.draw_classic_snoopy(draw, x, y)
        
        # Override arms for dancing pose
        arm_y = y + 18
        draw.line([x - 9, arm_y, x - 9, arm_y - 10], fill=0, width=2)  # Raised left arm
        draw.line([x + 9, arm_y, x + 9, arm_y - 10], fill=0, width=2)  # Raised right arm
        
        # Add some movement lines
        draw.line([x - 15, y + 5, x - 12, y + 8], fill=0, width=1)
        draw.line([x + 12, y + 5, x + 15, y + 8], fill=0, width=1)
        
    def draw_sleeping_snoopy(self, draw, x, y):
        """Draw sleeping Snoopy"""
        # Head
        head_width = 20
        head_height = 18
        draw.ellipse([x - head_width//2, y - head_height//2, 
                     x + head_width//2, y + head_height//2], 
                    fill=255, outline=0, width=2)
        
        # Long black nose
        nose_length = 10
        nose_width = 4
        nose_x = x + head_width//2 - 3
        nose_y = y + 1
        draw.ellipse([nose_x, nose_y, nose_x + nose_length, nose_y + nose_width], fill=0)
        
        # Ears
        ear_width = 8
        ear_height = 10
        draw.ellipse([x - head_width//2 - 4, y - head_height//2 - 3,
                     x - head_width//2 + 4, y - head_height//2 + 7],
                    fill=255, outline=0, width=1)
        draw.ellipse([x + head_width//2 - 4, y - head_height//2 - 3,
                     x + head_width//2 + 4, y - head_height//2 + 7],
                    fill=255, outline=0, width=1)
        
        # Closed eyes
        eye_y = y - 2
        draw.arc([x - 7, eye_y - 1, x - 3, eye_y + 3], 0, 180, fill=0, width=2)
        draw.arc([x + 3, eye_y - 1, x + 7, eye_y + 3], 0, 180, fill=0, width=2)
        
        # Body (lying down)
        body_width = 25
        body_height = 18
        draw.ellipse([x - body_width//2, y + 8, 
                     x + body_width//2, y + 8 + body_height], 
                    fill=255, outline=0, width=2)
        
        # Sleep bubbles
        for i in range(3):
            bubble_x = x + 15 + i * 8
            bubble_y = y - 5 - i * 3
            bubble_size = 6 - i * 2
            if bubble_size > 1:
                draw.ellipse([bubble_x, bubble_y, bubble_x + bubble_size, bubble_y + bubble_size], 
                           fill=255, outline=0, width=1)
        
    def draw_happy_snoopy(self, draw, x, y):
        """Draw happy Snoopy"""
        # Similar to classic but with happy expression
        self.draw_classic_snoopy(draw, x, y)
        
        # Override eyes for happy expression
        eye_y = y - 2
        # Happy eyes (curved)
        draw.arc([x - 7, eye_y - 1, x - 3, eye_y + 3], 0, 180, fill=0, width=2)
        draw.arc([x + 3, eye_y - 1, x + 7, eye_y + 3], 0, 180, fill=0, width=2)
        
        # Happy mouth
        mouth_y = y + 4
        draw.arc([x - 5, mouth_y - 2, x + 5, mouth_y + 2], 0, 180, fill=0, width=2)
        
    def load_web_images(self):
        """Load images from web sources"""
        logging.info("Attempting to load web images")
        web_images = []
        
        for img_info in WORKING_SNOOPY_IMAGES:
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
        
    def create_custom_drawings(self):
        """Create custom Snoopy drawings"""
        logging.info("Creating custom Snoopy drawings")
        custom_images = []
        
        poses = ['classic', 'dancing', 'sleeping', 'happy']
        
        for pose in poses:
            try:
                image = self.create_snoopy_drawing(pose)
                custom_images.append({
                    'name': f'Snoopy {pose.title()}',
                    'image': image,
                    'description': f'Custom {pose} Snoopy'
                })
                logging.info(f"Created custom drawing: {pose}")
            except Exception as e:
                logging.error(f"Error creating {pose} drawing: {e}")
                
        return custom_images
        
    def display_image(self, image_info):
        """Display image on e-paper display"""
        try:
            # Get the image
            image = image_info['image']
            
            # Add text overlay
            draw = ImageDraw.Draw(image)
            try:
                font_small = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 8)
            except:
                font_small = ImageFont.load_default()
                
            # Draw text background
            draw.rectangle([0, 0, self.width, 20], fill=255, outline=0, width=1)
            
            # Draw image name
            draw.text((5, 5), image_info['name'], font=font_small, fill=0)
            
            # Display the image
            self.epd.display(self.epd.getbuffer(image))
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
            
            # Load web images
            web_images = self.load_web_images()
            
            # Create custom drawings
            custom_images = self.create_custom_drawings()
            
            # Combine all images
            self.images = web_images + custom_images
            
            if not self.images:
                logging.error("No images available to display")
                return
                
            logging.info(f"Loaded {len(self.images)} images total")
            
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
    logging.info("Starting Snoopy Image Gallery")
    
    try:
        gallery = SnoopyImageGallery()
        gallery.run()
        
    except Exception as e:
        logging.error(f"Main error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 