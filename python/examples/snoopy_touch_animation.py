#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Snoopy Touch Animation for Waveshare 2.13" V4 Touch e-Paper Display
Created for Raspberry Pi Zero 2W

This program displays an animated Snoopy character that responds to touch input:
- Touch different areas to see different Snoopy animations
- Snoopy will dance, sleep, eat, and play based on where you touch
- The display updates with smooth animations
"""

import sys
import os
import time
import logging
import threading
from PIL import Image, ImageDraw, ImageFont
import traceback

# Set up paths
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic/2in13')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

from TP_lib import gt1151
from TP_lib import epd2in13_V4

logging.basicConfig(level=logging.DEBUG)

# Animation states
SNOOPY_STATES = {
    'idle': 0,
    'dancing': 1,
    'sleeping': 2,
    'eating': 3,
    'happy': 4,
    'surprised': 5
}

# Snoopy ASCII art frames for different animations
SNOOPY_FRAMES = {
    'idle': [
        """
    ,___,
   [O.o]/
   /)__)
  -"--"-
        """,
        """
    ,___,
   [O.o]/
   /)__)
  -"--"-
        """
    ],
    'dancing': [
        """
    ,___,
   [O.o]/
   /)__)  ~
  -"--"-
        """,
        """
    ,___,
   [O.o]/
   /)__)  ~
  -"--"-
        """,
        """
    ,___,
   [O.o]/
   /)__)  ~
  -"--"-
        """
    ],
    'sleeping': [
        """
    ,___,
   [-.-]z
   /)__)
  -"--"-
        """,
        """
    ,___,
   [-.-]Z
   /)__)
  -"--"-
        """
    ],
    'eating': [
        """
    ,___,
   [O.o]/
   /)__)  nom
  -"--"-
        """,
        """
    ,___,
   [O.o]/
   /)__)  nom nom
  -"--"-
        """
    ],
    'happy': [
        """
    ,___,
   [^_^]/
   /)__)
  -"--"-
        """,
        """
    ,___,
   [^_^]/
   /)__)  :)
  -"--"-
        """
    ],
    'surprised': [
        """
    ,___,
   [O_O]/
   /)__)
  -"--"-
        """,
        """
    ,___,
   [O_O]/
   /)__)  !!
  -"--"-
        """
    ]
}

class SnoopyAnimation:
    def __init__(self):
        self.epd = epd2in13_V4.EPD()
        self.gt = gt1151.GT1151()
        self.GT_Dev = gt1151.GT_Development()
        self.GT_Old = gt1151.GT_Development()
        
        # Display dimensions for 2.13" V4
        self.width = 122
        self.height = 250
        
        # Animation state
        self.current_state = 'idle'
        self.frame_index = 0
        self.animation_timer = 0
        self.state_duration = 0
        
        # Touch areas (simplified for 2.13" display)
        self.touch_areas = {
            'top': (0, 0, self.width, self.height//3),
            'middle': (0, self.height//3, self.width, 2*self.height//3),
            'bottom': (0, 2*self.height//3, self.width, self.height)
        }
        
        # Threading
        self.flag_t = 1
        self.touch_thread = None
        
    def init_display(self):
        """Initialize the e-paper display and touch controller"""
        logging.info("Initializing Snoopy Touch Animation")
        
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
        
    def get_touch_area(self, x, y):
        """Determine which area was touched"""
        if y < self.height // 3:
            return 'top'
        elif y < 2 * self.height // 3:
            return 'middle'
        else:
            return 'bottom'
            
    def handle_touch(self, x, y):
        """Handle touch input and change animation state"""
        area = self.get_touch_area(x, y)
        
        if area == 'top':
            self.current_state = 'dancing'
            self.state_duration = 50  # frames
            logging.info("Touch top area - Snoopy starts dancing!")
        elif area == 'middle':
            self.current_state = 'happy'
            self.state_duration = 30
            logging.info("Touch middle area - Snoopy is happy!")
        elif area == 'bottom':
            if self.current_state == 'sleeping':
                self.current_state = 'surprised'
                self.state_duration = 20
                logging.info("Touch bottom area - Snoopy is surprised!")
            else:
                self.current_state = 'sleeping'
                self.state_duration = 40
                logging.info("Touch bottom area - Snoopy goes to sleep!")
                
        self.frame_index = 0
        self.animation_timer = 0
        
    def draw_snoopy(self, draw, state, frame_idx):
        """Draw Snoopy character on the display"""
        # Get the current frame
        frames = SNOOPY_FRAMES[state]
        frame = frames[frame_idx % len(frames)]
        
        # Split frame into lines
        lines = frame.strip().split('\n')
        
        # Calculate starting position (center Snoopy)
        char_width = 8  # Approximate character width
        char_height = 12  # Approximate character height
        
        frame_width = max(len(line) for line in lines) * char_width
        frame_height = len(lines) * char_height
        
        start_x = (self.width - frame_width) // 2
        start_y = (self.height - frame_height) // 2
        
        # Draw each line of the ASCII art
        y_pos = start_y
        for line in lines:
            x_pos = start_x
            for char in line:
                if char != ' ':
                    # Draw character as a small rectangle
                    draw.rectangle([x_pos, y_pos, x_pos + char_width - 1, y_pos + char_height - 1], 
                                 fill=0, outline=0)
                x_pos += char_width
            y_pos += char_height
            
    def draw_ui_elements(self, draw):
        """Draw UI elements and instructions"""
        try:
            font_small = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 12)
        except:
            font_small = ImageFont.load_default()
            
        # Draw touch area indicators
        draw.text((5, 5), "Touch Top: Dance", font=font_small, fill=0)
        draw.text((5, self.height - 40), "Touch Bottom: Sleep/Wake", font=font_small, fill=0)
        draw.text((5, self.height//2 - 10), "Touch Middle: Happy", font=font_small, fill=0)
        
        # Draw current state
        state_text = f"State: {self.current_state}"
        draw.text((5, self.height - 20), state_text, font=font_small, fill=0)
        
    def update_animation(self):
        """Update animation state and frame"""
        self.animation_timer += 1
        
        # Update frame index for animation
        if self.animation_timer % 10 == 0:  # Change frame every 10 updates
            self.frame_index += 1
            
        # Check if state should return to idle
        if self.state_duration > 0:
            self.state_duration -= 1
            if self.state_duration <= 0:
                self.current_state = 'idle'
                self.frame_index = 0
                
    def run(self):
        """Main animation loop"""
        try:
            self.init_display()
            
            # Create base image
            image = Image.new('1', (self.width, self.height), 255)
            draw = ImageDraw.Draw(image)
            
            # Initial display
            self.epd.displayPartBaseImage(self.epd.getbuffer(image))
            self.epd.init(self.epd.PART_UPDATE)
            
            refresh_counter = 0
            last_touch_x = last_touch_y = 0
            
            logging.info("Starting Snoopy animation loop")
            
            while True:
                # Update animation
                self.update_animation()
                
                # Clear the image
                draw.rectangle([0, 0, self.width, self.height], fill=255)
                
                # Draw Snoopy
                self.draw_snoopy(draw, self.current_state, self.frame_index)
                
                # Draw UI elements
                self.draw_ui_elements(draw)
                
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
                            last_touch_x, last_touch_y = touch_x, touch_y
                            
                        self.GT_Dev.TouchpointFlag = 0
                
                # Update display periodically
                refresh_counter += 1
                if refresh_counter >= 20:  # Refresh every 20 loops
                    self.epd.displayPartial(self.epd.getbuffer(image))
                    refresh_counter = 0
                    
                # Small delay to prevent excessive CPU usage
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            logging.info("Animation interrupted by user")
            
        except Exception as e:
            logging.error(f"Animation error: {e}")
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
    logging.info("Starting Snoopy Touch Animation")
    
    try:
        snoopy = SnoopyAnimation()
        snoopy.run()
        
    except Exception as e:
        logging.error(f"Main error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 