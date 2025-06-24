# Simple Real-time Display for Waveshare 2.9 inch e-Paper
# Updates every second with time, crypto, weather, and system info
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../pic/2in9')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../pic')

# Search lib folder for display driver modules
sys.path.append('lib')
from . import epd2in9_V2
epd = epd2in9_V2.EPD_2IN9_V2()

from datetime import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import requests
import json
import psutil
import threading

# Set the fonts
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../pic')
font16 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 16)
font20 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 20)
font24 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 24)
font30 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 30)
font40 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 40)

# Set the colors
black = 'rgb(0,0,0)'
white = 'rgb(255,255,255)'

# Global data storage
data = {
    'time': '',
    'bitcoin_price': 'Loading...',
    'weather_temp': 'Loading...',
    'cpu_usage': '0%',
    'memory_usage': '0%',
    'uptime': '0:00:00'
}

def get_bitcoin_price():
    """Get Bitcoin price from CoinGecko (free, no API key needed)"""
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=3)
        if response.status_code == 200:
            price = response.json()['bitcoin']['usd']
            return f"${price:,.0f}"
        return "Error"
    except:
        return "Error"

def get_weather():
    """Get weather from Open-Meteo (free, no API key needed)"""
    try:
        # Default to New York coordinates - you can change these
        lat, lon = 40.7128, -74.0060
        url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&timezone=auto'
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            temp = response.json()['current']['temperature_2m']
            return f"{temp:.0f}°C"
        return "Error"
    except:
        return "Error"

def get_system_info():
    """Get system information"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Get uptime
        uptime_seconds = time.time() - psutil.boot_time()
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        uptime = f"{hours}:{minutes:02d}:{seconds:02d}"
        
        return f"{cpu_percent:.0f}%", f"{memory_percent:.0f}%", uptime
    except:
        return "0%", "0%", "0:00:00"

def update_data():
    """Update all data sources in parallel"""
    global data
    
    # Update time
    data['time'] = datetime.now().strftime('%H:%M:%S')
    
    # Update data in parallel
    threads = []
    
    def update_crypto():
        data['bitcoin_price'] = get_bitcoin_price()
    
    def update_weather():
        data['weather_temp'] = get_weather()
    
    def update_system():
        cpu, mem, uptime = get_system_info()
        data['cpu_usage'] = cpu
        data['memory_usage'] = mem
        data['uptime'] = uptime
    
    # Start threads
    for func in [update_crypto, update_weather, update_system]:
        thread = threading.Thread(target=func)
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

def create_display():
    """Create the display image"""
    # Create image with white background
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    
    # Draw header
    draw.rectangle((0, 0, 295, 40), fill=black)
    draw.text((10, 8), 'REAL-TIME MONITOR', font=font24, fill=white)
    
    # Draw time (large and prominent)
    draw.text((10, 50), f"TIME: {data['time']}", font=font40, fill=black)
    
    # Draw Bitcoin price
    draw.text((10, 100), f"Bitcoin: {data['bitcoin_price']}", font=font24, fill=black)
    
    # Draw weather
    draw.text((10, 130), f"Weather: {data['weather_temp']}", font=font24, fill=black)
    
    # Draw system info
    draw.text((10, 160), f"CPU: {data['cpu_usage']}", font=font20, fill=black)
    draw.text((10, 180), f"RAM: {data['memory_usage']}", font=font20, fill=black)
    draw.text((10, 200), f"Uptime: {data['uptime']}", font=font20, fill=black)
    
    # Draw update indicator
    draw.text((10, 220), f"Updated: {datetime.now().strftime('%H:%M:%S')}", font=font16, fill=black)
    
    return image

def run_display():
    """Main function to run the display"""
    print("Starting Simple Real-Time Display...")
    print("Press Ctrl+C to stop")
    
    # Initialize display
    epd.init()
    epd.Clear()
    
    try:
        while True:
            # Update data
            update_data()
            
            # Create and display image
            image = create_display()
            epd.display(epd.getbuffer(image))
            
            print(f"Updated at {data['time']} - BTC: {data['bitcoin_price']} - Weather: {data['weather_temp']}")
            
            # Wait 1 second
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping display...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        epd.module_exit()

if __name__ == "__main__":
    run_display() 