# Real-time Display for Waveshare 2.9 inch e-Paper
# Uses multiple free APIs to display various real-time data
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../pic/2in9')
icondir = os.path.join(picdir, 'icon')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../pic')

# Search lib folder for display driver modules
sys.path.append('lib')
from . import epd2in9_V2
epd = epd2in9_V2.EPD_2IN9_V2()

from datetime import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import traceback
import requests
import json
from io import BytesIO
import threading

# Set the fonts
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../pic')
font12 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 12)
font16 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 16)
font20 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 20)
font24 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 24)
font30 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 30)
font35 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 35)
font50 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 50)
font60 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 60)
font100 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 100)
font160 = ImageFont.truetype(os.path.join(fontdir, 'Font.ttc'), 160)

# Set the special fonts
font18_Roboto_Bold = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Bold.ttf'), 18)
font20_Roboto_Bold = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Bold.ttf'), 20)
font20_Roboto_Regular = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Regular.ttf'), 20)
font34_Roboto_Black = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Black.ttf'), 34)

# Set the colors
black = 'rgb(0,0,0)'
white = 'rgb(255,255,255)'
grey = 'rgb(235,235,235)'

# Global data storage
current_data = {
    'time': '',
    'date': '',
    'crypto_price': 'Loading...',
    'stock_price': 'Loading...',
    'weather_temp': 'Loading...',
    'weather_desc': 'Loading...',
    'ip_info': 'Loading...',
    'joke': 'Loading...',
    'quote': 'Loading...',
    'last_update': ''
}

# Free APIs to use
APIS = {
    'crypto': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
    'weather': 'https://api.open-meteo.com/v1/forecast?latitude=40.7128&longitude=-74.0060&current=temperature_2m,weather_code&timezone=auto',
    'ip': 'https://ipapi.co/json/',
    'joke': 'https://official-joke-api.appspot.com/random_joke',
    'quote': 'https://api.quotable.io/random',
    'stock': 'https://query1.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=1d'
}

def get_crypto_price():
    """Get Bitcoin price from CoinGecko (free, no API key needed)"""
    try:
        response = requests.get(APIS['crypto'], timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = data['bitcoin']['usd']
            return f"${price:,.0f}"
        return "Error"
    except:
        return "Error"

def get_weather():
    """Get weather from Open-Meteo (free, no API key needed)"""
    try:
        response = requests.get(APIS['weather'], timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = data['current']['temperature_2m']
            weather_code = data['current']['weather_code']
            
            # Simple weather description mapping
            weather_descriptions = {
                0: "Clear", 1: "Partly Cloudy", 2: "Cloudy", 3: "Overcast",
                45: "Foggy", 48: "Foggy", 51: "Light Drizzle", 53: "Drizzle",
                55: "Heavy Drizzle", 61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
                71: "Light Snow", 73: "Snow", 75: "Heavy Snow", 95: "Thunderstorm"
            }
            
            desc = weather_descriptions.get(weather_code, "Unknown")
            return f"{temp:.0f}°C", desc
        return "Error", "Error"
    except:
        return "Error", "Error"

def get_ip_info():
    """Get IP location info (free, no API key needed)"""
    try:
        response = requests.get(APIS['ip'], timeout=5)
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', 'Unknown')
            country = data.get('country_name', 'Unknown')
            return f"{city}, {country}"
        return "Error"
    except:
        return "Error"

def get_joke():
    """Get a random joke (free, no API key needed)"""
    try:
        response = requests.get(APIS['joke'], timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data['setup'][:50] + "..." if len(data['setup']) > 50 else data['setup']
        return "Error"
    except:
        return "Error"

def get_quote():
    """Get a random quote (free, no API key needed)"""
    try:
        response = requests.get(APIS['quote'], timeout=5)
        if response.status_code == 200:
            data = response.json()
            quote = data['content'][:60] + "..." if len(data['content']) > 60 else data['content']
            author = data['author']
            return f'"{quote}" - {author}'
        return "Error"
    except:
        return "Error"

def get_stock_price():
    """Get Apple stock price from Yahoo Finance (free, no API key needed)"""
    try:
        response = requests.get(APIS['stock'], timeout=5)
        if response.status_code == 200:
            data = response.json()
            price = data['chart']['result'][0]['meta']['regularMarketPrice']
            return f"${price:.2f}"
        return "Error"
    except:
        return "Error"

def update_data():
    """Update all data sources"""
    global current_data
    
    # Update time and date
    now = datetime.now()
    current_data['time'] = now.strftime('%H:%M:%S')
    current_data['date'] = now.strftime('%Y-%m-%d')
    current_data['last_update'] = now.strftime('%H:%M:%S')
    
    # Update data in parallel threads for faster response
    threads = []
    
    def update_crypto():
        current_data['crypto_price'] = get_crypto_price()
    
    def update_weather():
        temp, desc = get_weather()
        current_data['weather_temp'] = temp
        current_data['weather_desc'] = desc
    
    def update_ip():
        current_data['ip_info'] = get_ip_info()
    
    def update_joke():
        current_data['joke'] = get_joke()
    
    def update_quote():
        current_data['quote'] = get_quote()
    
    def update_stock():
        current_data['stock_price'] = get_stock_price()
    
    # Start threads
    for func in [update_crypto, update_weather, update_ip, update_joke, update_quote, update_stock]:
        thread = threading.Thread(target=func)
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

def create_display_image():
    """Create the display image with all the data"""
    # Create a new image with white background
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    
    # Draw header
    draw.rectangle((0, 0, 295, 30), fill=black)
    draw.text((10, 5), 'REAL-TIME DATA DISPLAY', font=font20_Roboto_Bold, fill=white)
    
    # Draw time and date
    draw.text((10, 35), f"Time: {current_data['time']}", font=font16, fill=black)
    draw.text((10, 55), f"Date: {current_data['date']}", font=font16, fill=black)
    
    # Draw crypto price
    draw.text((10, 80), f"Bitcoin: {current_data['crypto_price']}", font=font16, fill=black)
    
    # Draw stock price
    draw.text((10, 100), f"AAPL Stock: {current_data['stock_price']}", font=font16, fill=black)
    
    # Draw weather
    draw.text((10, 120), f"Weather: {current_data['weather_temp']} - {current_data['weather_desc']}", font=font16, fill=black)
    
    # Draw IP location
    draw.text((10, 140), f"Location: {current_data['ip_info']}", font=font16, fill=black)
    
    # Draw joke
    draw.text((10, 160), f"Joke: {current_data['joke']}", font=font12, fill=black)
    
    # Draw quote
    draw.text((10, 180), f"Quote: {current_data['quote']}", font=font12, fill=black)
    
    # Draw last update time
    draw.text((10, 200), f"Last Update: {current_data['last_update']}", font=font12, fill=black)
    
    return image

def display_error(error_source):
    """Display an error message"""
    print(f'Error in the {error_source} request.')
    error_image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(error_image)
    draw.text((5, 5), f'{error_source} ERROR', font=font20, fill=black)
    draw.text((5, 30), 'Retrying in 5 seconds', font=font20, fill=black)
    current_time = datetime.now().strftime('%H:%M:%S')
    draw.text((5, 55), f'Last Refresh: {current_time}', font=font20, fill=black)
    
    # Save and display error
    error_image_file = os.path.join(picdir, 'error.png')
    error_image.save(error_image_file)
    error_image.close()
    
    # Display error on screen
    epd.display(epd.getbuffer(error_image))
    time.sleep(5)

def run_real_time_display():
    """Main function to run the real-time display"""
    print("Starting Real-Time Display...")
    
    # Initialize the display
    epd.init()
    epd.Clear()
    
    try:
        while True:
            print("Updating data...")
            update_data()
            
            # Create and display the image
            image = create_display_image()
            epd.display(epd.getbuffer(image))
            
            print(f"Display updated at {current_data['last_update']}")
            
            # Wait 1 second before next update
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Display stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        display_error('SYSTEM')
    finally:
        epd.module_exit()

if __name__ == "__main__":
    run_real_time_display() 