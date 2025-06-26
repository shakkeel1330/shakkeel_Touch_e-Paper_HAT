#!/usr/bin/env python3
import sys
import os
import time
import random
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import logging

# Add the lib path for the Waveshare display
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

try:
    from waveshare_epd import epd2in13_V4
except ImportError:
    print("Waveshare library not found. Make sure you've installed the Touch_e-Paper_HAT library.")
    sys.exit(1)

# Configuration
REFRESH_INTERVAL = 300  # 5 minutes in seconds
FONT_SIZE = 12
TITLE_FONT_SIZE = 15
REQUEST_TIMEOUT = 10

# API endpoints
HAIKU_APIS = [
    {
        "name": "HaikuDB",
        "url": "https://haiku-json-db.herokuapp.com/haiku/random",
        "parser": "haikudb"
    }
]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Local backup haiku collection (fallback if APIs fail)
LOCAL_HAIKU = [
    {
        "lines": ["Morning dew falls soft", "On petals kissed by sunlight", "Spring whispers awake"],
        "author": "Digital Poet",
        "theme": "Spring"
    },
    {
        "lines": ["Autumn leaves spiral", "Dancing on the gentle breeze", "Time's golden letter"],
        "author": "Digital Poet", 
        "theme": "Autumn"
    },
    {
        "lines": ["Silent snow blankets", "The sleeping earth in white dreams", "Winter's quiet song"],
        "author": "Digital Poet",
        "theme": "Winter"
    },
    {
        "lines": ["Ocean waves crash down", "Against the weathered sea rocks", "Eternal rhythm"],
        "author": "Digital Poet",
        "theme": "Nature"
    },
    {
        "lines": ["Cherry blossoms bloom", "Brief beauty on morning wind", "Moments drift away"],
        "author": "Digital Poet",
        "theme": "Spring"
    },
    {
        "lines": ["Code flows like water", "Through circuits of silicon", "Digital rivers"],
        "author": "Digital Poet",
        "theme": "Technology"
    },
    {
        "lines": ["E-ink slowly turns", "Black and white thoughts crystallize", "Poetry in bytes"],
        "author": "Digital Poet",
        "theme": "Technology"
    },
    {
        "lines": ["Coffee steam rises", "Morning ritual awakens", "Day begins with warmth"],
        "author": "Digital Poet",
        "theme": "Daily Life"
    },
    {
        "lines": ["Heart beats like thunder", "Love arrives on silent feet", "Soul recognizes"],
        "author": "Digital Poet",
        "theme": "Love"
    },
    {
        "lines": ["Stars shine through darkness", "Each one a distant beacon", "Hope lights the night sky"],
        "author": "Digital Poet",
        "theme": "Hope"
    }
]

class HaikuDisplay:
    def __init__(self):
        self.epd = epd2in13_V4.EPD()
        self.width = 122
        self.height = 250
        self.api_failures = 0
        self.max_api_failures = 3
        
    def init_display(self):
        """Initialize the e-paper display"""
        try:
            logger.info("Initializing display...")
            self.epd.init()
            self.epd.Clear(0xFF)
            logger.info("Display initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            return False
    
    def fetch_haiku_from_api(self):
        """Fetch a haiku from external APIs"""
        if self.api_failures >= self.max_api_failures:
            logger.info("Too many API failures, using local haiku")
            return None
            
        for api in HAIKU_APIS:
            try:
                logger.info(f"Fetching haiku from {api['name']}...")
                response = requests.get(api['url'], timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                data = response.json()
                haiku = self.parse_api_response(data, api['parser'])
                
                if haiku:
                    logger.info(f"Successfully fetched haiku from {api['name']}")
                    self.api_failures = 0  # Reset failure counter on success
                    return haiku
                    
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch from {api['name']}: {e}")
                continue
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from {api['name']}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error with {api['name']}: {e}")
                continue
        
        # If all APIs fail, increment failure counter
        self.api_failures += 1
        logger.warning(f"All APIs failed (attempt {self.api_failures}/{self.max_api_failures})")
        return None
    
    def parse_api_response(self, data, parser_type):
        """Parse different API response formats"""
        try:
            if parser_type == "haikudb":
                # Expected format: {"poem": "line1\nline2\nline3", "author": "Name"}
                if "poem" in data:
                    lines = data["poem"].split('\n')
                    if len(lines) >= 3:
                        return {
                            "lines": lines[:3],  # Take first 3 lines
                            "author": data.get("author", "Unknown"),
                            "theme": "Classic",
                            "source": "HaikuDB"
                        }
                        
            return None
        except Exception as e:
            logger.error(f"Error parsing API response: {e}")
            return None
    
    def get_local_haiku(self):
        """Get a random haiku from local collection"""
        haiku = random.choice(LOCAL_HAIKU)
        haiku["source"] = "Local"
        return haiku
    
    def get_haiku(self):
        """Get a haiku from API or local collection"""
        # Try API first
        haiku = self.fetch_haiku_from_api()
        
        # Fall back to local if API fails
        if not haiku:
            haiku = self.get_local_haiku()
            
        return haiku
    
    def clean_text(self, text):
        """Clean text for display (remove extra spaces, etc.)"""
        if not text:
            return ""
        return ' '.join(text.split())
    
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
        header_bbox = draw.textbbox((0, 0), header, font=title_font)
        header_width = header_bbox[2] - header_bbox[0]
        header_x = (self.width - header_width) // 2
        draw.text((header_x, y_position), header, font=title_font, fill=0)
        y_position += 25
        
        # Draw decorative elements
        center_x = self.width // 2
        draw.ellipse([center_x-2, y_position, center_x+2, y_position+4], fill=0)
        y_position += 15
        
        # Draw the three haiku lines with proper spacing
        lines = haiku_data.get("lines", ["Error", "Loading", "Haiku"])
        line_spacing = 20
        
        for i, line in enumerate(lines):
            # Clean and center each line
            clean_line = self.clean_text(line)
            if len(clean_line) > 18:  # Wrap long lines
                clean_line = clean_line[:18] + "..."
                
            line_bbox = draw.textbbox((0, 0), clean_line, font=text_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (self.width - line_width) // 2
            draw.text((line_x, y_position), clean_line, font=text_font, fill=0)
            y_position += line_spacing
            
            # Add subtle spacing dots between lines
            if i < len(lines) - 1:
                draw.ellipse([center_x-1, y_position-8, center_x+1, y_position-6], fill=0)
        
        y_position += 15
        
        # Draw author info
        author = haiku_data.get("author", "Unknown")
        if len(author) > 15:
            author = author[:15] + "..."
        author_info = f"— {author}"
        
        author_bbox = draw.textbbox((0, 0), author_info, font=small_font)
        author_width = author_bbox[2] - author_bbox[0]
        author_x = (self.width - author_width) // 2
        draw.text((author_x, y_position), author_info, font=small_font, fill=0)
        y_position += 15
        
        # Draw source indicator
        source = haiku_data.get("source", "Unknown")
        theme = haiku_data.get("theme", "")
        if theme and theme != "Classic":
            source_info = f"~ {theme} ~"
        else:
            source_info = f"~ {source} ~"
            
        source_bbox = draw.textbbox((0, 0), source_info, font=small_font)
        source_width = source_bbox[2] - source_bbox[0]
        source_x = (self.width - source_width) // 2
        draw.text((source_x, y_position), source_info, font=small_font, fill=0)
        
        # Add timestamp at bottom
        timestamp = time.strftime("%H:%M")
        timestamp_bbox = draw.textbbox((0, 0), timestamp, font=small_font)
        timestamp_width = timestamp_bbox[2] - timestamp_bbox[0]
        timestamp_x = (self.width - timestamp_width) // 2
        draw.text((timestamp_x, self.height - 18), timestamp, font=small_font, fill=0)
        
        return image
    
    def display_image(self, image):
        """Display the image on the e-paper display"""
        try:
            logger.info("Updating display...")
            self.epd.display(self.epd.getbuffer(image))
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
            "Fetching poetry",
            "from the cloud",
            "",
            "Fresh haiku every",
            "5 minutes!"
        ]
        
        y_pos = 20
        for i, line in enumerate(lines):
            if line:
                font_to_use = title_font if i == 0 else font
                line_bbox = draw.textbbox((0, 0), line, font=font_to_use)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = (self.width - line_width) // 2
                draw.text((line_x, y_pos), line, font=font_to_use, fill=0)
            y_pos += 16
        
        self.display_image(image)
        time.sleep(3)  # Show startup message for 3 seconds
    
    def run(self):
        """Main loop to fetch and display haiku"""
        if not self.init_display():
            logger.error("Failed to initialize display. Exiting.")
            return
        
        # Show startup message
        self.display_startup_message()
        
        logger.info("Starting haiku display loop...")
        
        while True:
            try:
                # Get a haiku (from API or local)
                haiku_data = self.get_haiku()
                logger.info(f"Displaying haiku from: {haiku_data.get('source', 'Unknown')}")
                
                # Create and display the haiku image
                image = self.create_haiku_image(haiku_data)
                self.display_image(image)
                
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