#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Snoopy Touch Animation V2 for Waveshare 2.13" V4 Touch e-Paper Display
Created for Raspberry Pi Zero 2W

This program displays an animated Snoopy character that responds to touch input:
- Touch different areas to see different Snoopy animations
- Snoopy will dance, sleep, eat, and play based on where you touch
- Uses geometric shapes for better visual quality on e-paper
"""

import sys
import os
import time
import logging
import threading
import math
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

class SnoopyAnimationV2:
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
        
        # Snoopy position and animation parameters
        self.snoopy_x = self.width // 2
        self.snoopy_y = self.height // 2
        self.dance_offset = 0
        self.sleep_bubble_size = 0
        
        # Threading
        self.flag_t = 1
        self.touch_thread = None
        
    def init_display(self):
        """Initialize the e-paper display and touch controller"""
        logging.info("Initializing Snoopy Touch Animation V2")
        
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
            self.state_duration = 60  # frames
            logging.info("Touch top area - Snoopy starts dancing!")
        elif area == 'middle':
            self.current_state = 'happy'
            self.state_duration = 40
            logging.info("Touch middle area - Snoopy is happy!")
        elif area == 'bottom':
            if self.current_state == 'sleeping':
                self.current_state = 'surprised'
                self.state_duration = 30
                logging.info("Touch bottom area - Snoopy is surprised!")
            else:
                self.current_state = 'sleeping'
                self.state_duration = 50
                logging.info("Touch bottom area - Snoopy goes to sleep!")
                
        self.frame_index = 0
        self.animation_timer = 0
        
    def draw_snoopy_head(self, draw, x, y, state):
        """Draw Snoopy's head"""
        # Head (white circle)
        head_radius = 15
        draw.ellipse([x - head_radius, y - head_radius, 
                     x + head_radius, y + head_radius], 
                    fill=255, outline=0, width=2)
        
        # Ears
        ear_radius = 8
        draw.ellipse([x - head_radius - 5, y - head_radius - 5,
                     x - head_radius + 5, y - head_radius + 5],
                    fill=255, outline=0, width=1)
        draw.ellipse([x + head_radius - 5, y - head_radius - 5,
                     x + head_radius + 5, y - head_radius + 5],
                    fill=255, outline=0, width=1)
        
        # Eyes based on state
        if state == 'sleeping':
            # Closed eyes
            draw.line([x - 8, y - 3, x - 4, y - 3], fill=0, width=2)
            draw.line([x + 4, y - 3, x + 8, y - 3], fill=0, width=2)
        elif state == 'surprised':
            # Surprised eyes (circles)
            draw.ellipse([x - 10, y - 5, x - 6, y - 1], fill=0)
            draw.ellipse([x + 6, y - 5, x + 10, y - 1], fill=0)
        elif state == 'happy':
            # Happy eyes (curved lines)
            draw.arc([x - 10, y - 5, x - 6, y - 1], 0, 180, fill=0, width=2)
            draw.arc([x + 6, y - 5, x + 10, y - 1], 0, 180, fill=0, width=2)
        else:
            # Normal eyes
            draw.ellipse([x - 8, y - 4, x - 4, y], fill=0)
            draw.ellipse([x + 4, y - 4, x + 8, y], fill=0)
        
        # Nose
        nose_y = y + 2
        draw.ellipse([x - 2, nose_y, x + 2, nose_y + 4], fill=0)
        
    def draw_snoopy_body(self, draw, x, y, state):
        """Draw Snoopy's body"""
        # Body (white oval)
        body_width = 20
        body_height = 25
        draw.ellipse([x - body_width//2, y, 
                     x + body_width//2, y + body_height], 
                    fill=255, outline=0, width=2)
        
        # Arms based on state
        if state == 'dancing':
            # Dancing arms (moving)
            arm_offset = math.sin(self.animation_timer * 0.3) * 5
            draw.line([x - body_width//2, y + 5, 
                      x - body_width//2 - 8, y + 5 + arm_offset], 
                     fill=0, width=3)
            draw.line([x + body_width//2, y + 5, 
                      x + body_width//2 + 8, y + 5 - arm_offset], 
                     fill=0, width=3)
        elif state == 'happy':
            # Happy arms (up)
            draw.line([x - body_width//2, y + 5, 
                      x - body_width//2 - 6, y + 5 - 8], 
                     fill=0, width=3)
            draw.line([x + body_width//2, y + 5, 
                      x + body_width//2 + 6, y + 5 - 8], 
                     fill=0, width=3)
        else:
            # Normal arms
            draw.line([x - body_width//2, y + 5, 
                      x - body_width//2 - 6, y + 5 + 6], 
                     fill=0, width=3)
            draw.line([x + body_width//2, y + 5, 
                      x + body_width//2 + 6, y + 5 + 6], 
                     fill=0, width=3)
        
        # Legs
        leg_y = y + body_height
        draw.line([x - 5, leg_y, x - 5, leg_y + 12], fill=0, width=3)
        draw.line([x + 5, leg_y, x + 5, leg_y + 12], fill=0, width=3)
        
        # Feet
        draw.ellipse([x - 8, leg_y + 10, x - 2, leg_y + 16], fill=0)
        draw.ellipse([x + 2, leg_y + 10, x + 8, leg_y + 16], fill=0)
        
    def draw_sleep_bubbles(self, draw, x, y):
        """Draw sleep bubbles when Snoopy is sleeping"""
        bubble_size = int(5 + math.sin(self.animation_timer * 0.2) * 3)
        bubble_x = x + 20
        bubble_y = y - 10
        
        # Draw multiple bubbles
        for i in range(3):
            offset = i * 8
            size = bubble_size - i * 2
            if size > 0:
                draw.ellipse([bubble_x + offset, bubble_y - offset, 
                            bubble_x + offset + size, bubble_y - offset + size], 
                           fill=255, outline=0, width=1)
        
    def draw_speech_bubble(self, draw, x, y, text):
        """Draw a speech bubble with text"""
        # Bubble background
        bubble_width = len(text) * 6 + 10
        bubble_height = 20
        bubble_x = x + 15
        bubble_y = y - 30
        
        # Bubble shape
        draw.ellipse([bubble_x, bubble_y, 
                     bubble_x + bubble_width, bubble_y + bubble_height], 
                    fill=255, outline=0, width=2)
        
        # Tail
        draw.polygon([(bubble_x + 5, bubble_y + bubble_height),
                     (bubble_x + 10, bubble_y + bubble_height + 5),
                     (bubble_x + 15, bubble_y + bubble_height)], 
                    fill=255, outline=0)
        
        # Text
        try:
            font_small = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 10)
        except:
            font_small = ImageFont.load_default()
            
        draw.text((bubble_x + 5, bubble_y + 5), text, font=font_small, fill=0)
        
    def draw_snoopy(self, draw, state):
        """Draw Snoopy character based on current state"""
        # Calculate position with dance offset
        x = self.snoopy_x
        y = self.snoopy_y
        
        if state == 'dancing':
            # Add dance movement
            x += int(math.sin(self.animation_timer * 0.4) * 3)
            y += int(math.cos(self.animation_timer * 0.3) * 2)
        
        # Draw body first (behind head)
        self.draw_snoopy_body(draw, x, y + 15, state)
        
        # Draw head
        self.draw_snoopy_head(draw, x, y, state)
        
        # Draw sleep bubbles if sleeping
        if state == 'sleeping':
            self.draw_sleep_bubbles(draw, x, y)
        
        # Draw speech bubble based on state
        if state == 'happy':
            self.draw_speech_bubble(draw, x, y, "Yay!")
        elif state == 'surprised':
            self.draw_speech_bubble(draw, x, y, "Oh!")
        elif state == 'dancing':
            self.draw_speech_bubble(draw, x, y, "~")
            
    def draw_ui_elements(self, draw):
        """Draw UI elements and instructions"""
        try:
            font_small = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 10)
        except:
            font_small = ImageFont.load_default()
            
        # Draw touch area indicators
        draw.text((2, 2), "Touch Top: Dance", font=font_small, fill=0)
        draw.text((2, self.height - 35), "Touch Bottom: Sleep/Wake", font=font_small, fill=0)
        draw.text((2, self.height//2 - 5), "Touch Middle: Happy", font=font_small, fill=0)
        
        # Draw current state
        state_text = f"State: {self.current_state}"
        draw.text((2, self.height - 15), state_text, font=font_small, fill=0)
        
        # Draw touch area dividers
        draw.line([(0, self.height//3), (self.width, self.height//3)], fill=0, width=1)
        draw.line([(0, 2*self.height//3), (self.width, 2*self.height//3)], fill=0, width=1)
        
    def update_animation(self):
        """Update animation state and frame"""
        self.animation_timer += 1
        
        # Update frame index for animation
        if self.animation_timer % 8 == 0:  # Change frame every 8 updates
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
            
            logging.info("Starting Snoopy animation loop")
            
            while True:
                # Update animation
                self.update_animation()
                
                # Clear the image
                draw.rectangle([0, 0, self.width, self.height], fill=255)
                
                # Draw Snoopy
                self.draw_snoopy(draw, self.current_state)
                
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
                            
                        self.GT_Dev.TouchpointFlag = 0
                
                # Update display periodically
                refresh_counter += 1
                if refresh_counter >= 15:  # Refresh every 15 loops
                    self.epd.displayPartial(self.epd.getbuffer(image))
                    refresh_counter = 0
                    
                # Small delay to prevent excessive CPU usage
                time.sleep(0.06)
                
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
    logging.info("Starting Snoopy Touch Animation V2")
    
    try:
        snoopy = SnoopyAnimationV2()
        snoopy.run()
        
    except Exception as e:
        logging.error(f"Main error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 