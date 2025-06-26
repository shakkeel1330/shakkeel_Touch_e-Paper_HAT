#!/usr/bin/env python3
import sys
import os
import time
import random
from PIL import Image, ImageDraw, ImageFont
import logging

# Add the correct lib path for YOUR specific Touch e-Paper HAT
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

# Also try the current directory lib
current_libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(current_libdir):
    sys.path.append(current_libdir)

try:
    # Import using the correct library structure for your model
    from TP_lib import epd2in13_V4
    print("Successfully imported TP_lib.epd2in13_V4")
except ImportError:
    print("TP_lib not found. Make sure you've copied the lib directory from Touch_e-Paper_HAT.")
    print("Expected path: ~/shakkeel_Touch_e-Paper_HAT/python/lib")
    sys.exit(1)

# Configuration
REFRESH_INTERVAL = 300  # 5 minutes in seconds
FONT_SIZE = 13
TITLE_FONT_SIZE = 15

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Haiku collection organized by themes
HAIKU_THEMES = {
    "nature": [
        {
            "lines": ["Morning dew falls soft", "On petals kissed by sunlight", "Spring whispers awake"],
            "season": "Spring"
        },
        {
            "lines": ["Autumn leaves spiral", "Dancing on the gentle breeze", "Time's golden letter"],
            "season": "Autumn"
        },
        {
            "lines": ["Silent snow blankets", "The sleeping earth in white dreams", "Winter's quiet song"],
            "season": "Winter"
        },
        {
            "lines": ["Ocean waves crash down", "Against the weathered sea rocks", "Eternal rhythm"],
            "season": "Summer"
        },
        {
            "lines": ["Cherry blossoms bloom", "Brief beauty on morning wind", "Moments drift away"],
            "season": "Spring"
        },
        {
            "lines": ["Mountain peak stands tall", "Crowned with clouds and morning mist", "Ancient and serene"],
            "season": "All"
        }
    ],
    "technology": [
        {
            "lines": ["Code flows like water", "Through circuits of silicon", "Digital rivers"],
            "season": "Digital"
        },
        {
            "lines": ["Screen light flickers soft", "Pixels dance in binary", "Modern meditation"],
            "season": "Digital"
        },
        {
            "lines": ["E-ink slowly turns", "Black and white thoughts crystallize", "Poetry in bytes"],
            "season": "Digital"
        },
        {
            "lines": ["WiFi signals float", "Invisible connections", "Binding distant hearts"],
            "season": "Digital"
        }
    ],
    "daily_life": [
        {
            "lines": ["Coffee steam rises", "Morning ritual awakens", "Day begins with warmth"],
            "season": "Daily"
        },
        {
            "lines": ["Books pile on the shelf", "Stories waiting to be read", "Adventure beckons"],
            "season": "Daily"
        },
        {
            "lines": ["Rain taps the window", "Office workers hurry past", "City symphony"],
            "season": "Daily"
        },
        {
            "lines": ["Clock ticks on the wall", "Moments passing like soft rain", "Time's gentle reminder"],
            "season": "Daily"
        },
        {
            "lines": ["Candle flame dances", "Shadows play on evening walls", "Peaceful solitude"],
            "season": "Daily"
        }
    ],
    "emotions": [
        {
            "lines": ["Heart beats like thunder", "Love arrives on silent feet", "Soul recognizes"],
            "season": "Feeling"
        },
        {
            "lines": ["Laughter bubbles up", "Joy spills over like spring rain", "Happiness blooms bright"],
            "season": "Feeling"
        },
        {
            "lines": ["Quiet contemplation", "Mind settles like evening lake", "Peace finds its home"],
            "season": "Feeling"
        },
        {
            "lines": ["Dreams float on night air", "Tomorrow's hopes take gentle flight", "Sleep carries wishes"],
            "season": "Feeling"
        }
    ],
    "seasons": [
        {
            "lines": ["First green shoots appear", "Through the last patches of snow", "Hope breaks winter's grip"],
            "season": "Spring"
        },
        {
            "lines": ["Cicadas singing", "Summer heat shimmers on roads", "Long days stretch lazy"],
            "season": "Summer"
        },
        {
            "lines": ["Harvest moon rises", "Fields of gold bow to cool breeze", "Autumn's gentle hand"],
            "season": "Autumn"
        },
        {
            "lines": ["Frost paints the windows", "Morning breath visible white", "Winter's artistry"],
            "season": "Winter"
        }
    ]
}

class HaikuDisplay:
    def __init__(self):
        self.epd = epd2in13_V4.EPD()
        self.width = 122
        self.height = 250
        
    def init_display(self):
        """Initialize the e-paper display"""
        try:
            logger.info("Initializing display...")
            # Use the correct initialization method for your model
            self.epd.init(self.epd.FULL_UPDATE)
            self.epd.Clear(0xFF)
            logger.info("Display initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            return False
    
    def get_random_haiku(self):
        """Get a random haiku from the collection"""
        # Choose a random theme
        theme = random.choice(list(HAIKU_THEMES.keys()))
        haiku = random.choice(HAIKU_THEMES[theme])
        
        return {
            "theme": theme.replace("_", " ").title(),
            "lines": haiku["lines"],
            "season": haiku["season"]
        }
    
    def create_haiku_image(self, haiku_data):
        """Create an image with the haiku text"""
        # Create a new image with white background
        image = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)
        
        try:
            # Try to load nice fonts, fall back to default if not available
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', TITLE_FONT_SIZE)
            text_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', FONT_SIZE)
            small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', FONT_SIZE-2)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw elegant border
        draw.rectangle([3, 3, self.width-4, self.height-4], outline=0, width=2)
        draw.rectangle([6, 6, self.width-7, self.height-7], outline=0, width=1)
        
        y_position = 20
        
        # Draw "HAIKU" header
        header = "HAIKU"
        try:
            header_bbox = draw.textbbox((0, 0), header, font=title_font)
            header_width = header_bbox[2] - header_bbox[0]
        except:
            # Fallback for older PIL versions
            header_width, _ = title_font.getsize(header)
        
        header_x = (self.width - header_width) // 2
        draw.text((header_x, y_position), header, font=title_font, fill=0)
        y_position += 25
        
        # Draw decorative elements
        center_x = self.width // 2
        draw.ellipse([center_x-2, y_position, center_x+2, y_position+4], fill=0)
        y_position += 15
        
        # Draw the three haiku lines with proper spacing
        lines = haiku_data["lines"]
        line_spacing = 22
        
        for i, line in enumerate(lines):
            # Center each line
            try:
                line_bbox = draw.textbbox((0, 0), line, font=text_font)
                line_width = line_bbox[2] - line_bbox[0]
            except:
                line_width, _ = text_font.getsize(line)
                
            line_x = (self.width - line_width) // 2
            draw.text((line_x, y_position), line, font=text_font, fill=0)
            y_position += line_spacing
            
            # Add subtle spacing dots between lines
            if i < len(lines) - 1:
                draw.ellipse([center_x-1, y_position-8, center_x+1, y_position-6], fill=0)
        
        y_position += 15
        
        # Draw theme/season info
        theme_info = f"~ {haiku_data['season']} ~"
        try:
            theme_bbox = draw.textbbox((0, 0), theme_info, font=small_font)
            theme_width = theme_bbox[2] - theme_bbox[0]
        except:
            theme_width, _ = small_font.getsize(theme_info)
            
        theme_x = (self.width - theme_width) // 2
        draw.text((theme_x, y_position), theme_info, font=small_font, fill=0)
        
        # Add timestamp at bottom
        timestamp = time.strftime("%H:%M")
        try:
            timestamp_bbox = draw.textbbox((0, 0), timestamp, font=small_font)
            timestamp_width = timestamp_bbox[2] - timestamp_bbox[0]
        except:
            timestamp_width, _ = small_font.getsize(timestamp)
            
        timestamp_x = (self.width - timestamp_width) // 2
        draw.text((timestamp_x, self.height - 18), timestamp, font=small_font, fill=0)
        
        return image
    
    def display_image(self, image):
        """Display the image on the e-paper display"""
        try:
            logger.info("Updating display...")
            # Use the correct display method for your model
            self.epd.displayPartBaseImage(self.epd.getbuffer(image))
            logger.info("Display updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to update display: {e}")
            return False
    
    def display_startup_message(self):
        """Display a startup message"""
        image = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', FONT_SIZE)
            title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', TITLE_FONT_SIZE)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        # Draw border
        draw.rectangle([3, 3, self.width-4, self.height-4], outline=0, width=2)
        
        # Draw startup message
        lines = [
            "HAIKU DISPLAY",
            "",
            "Starting up...",
            "",
            "Fresh poems every",
            "5 minutes",
            "",
            "Enjoy the poetry!"
        ]
        
        y_pos = 25
        for i, line in enumerate(lines):
            if line:
                font_to_use = title_font if i == 0 else font
                try:
                    line_bbox = draw.textbbox((0, 0), line, font=font_to_use)
                    line_width = line_bbox[2] - line_bbox[0]
                except:
                    line_width, _ = font_to_use.getsize(line)
                    
                line_x = (self.width - line_width) // 2
                draw.text((line_x, y_pos), line, font=font_to_use, fill=0)
            y_pos += 18
        
        self.display_image(image)
        time.sleep(3)  # Show startup message for 3 seconds
    
    def run(self):
        """Main loop to generate and display haiku"""
        if not self.init_display():
            logger.error("Failed to initialize display. Exiting.")
            return
        
        # Show startup message
        self.display_startup_message()
        
        # Switch to partial update mode for better performance
        try:
            self.epd.init(self.epd.PART_UPDATE)
        except:
            logger.warning("Could not switch to partial update mode")
        
        logger.info("Starting haiku display loop...")
        
        refresh_count = 0
        
        while True:
            try:
                # Generate a random haiku
                haiku_data = self.get_random_haiku()
                logger.info(f"Displaying haiku from theme: {haiku_data['theme']}")
                
                # Create and display the haiku image
                image = self.create_haiku_image(haiku_data)
                
                # Every 10th refresh, do a full refresh to prevent ghosting
                if refresh_count % 10 == 0:
                    logger.info("Performing full refresh to prevent ghosting")
                    self.epd.init(self.epd.FULL_UPDATE)
                    self.epd.displayPartBaseImage(self.epd.getbuffer(image))
                    self.epd.init(self.epd.PART_UPDATE)
                else:
                    # Use partial update for faster refresh
                    try:
                        self.epd.displayPartial(self.epd.getbuffer(image))
                    except:
                        # Fallback to base image method
                        self.epd.displayPartBaseImage(self.epd.getbuffer(image))
                
                refresh_count += 1
                
                # Wait for next refresh
                logger.info(f"Waiting {REFRESH_INTERVAL} seconds before next haiku...")
                time.sleep(REFRESH_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying
        
        # Clean up
        try:
            self.epd.sleep()
        except:
            pass

if __name__ == "__main__":
    display = HaikuDisplay()
    display.run()