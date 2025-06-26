# Raspberry Pi Haiku Display Setup

Transform your Raspberry Pi Zero 2W and Waveshare 2.13" touch eink display into a beautiful haiku poetry generator! This setup creates a self-contained system that displays a new haiku every 5 minutes.

## 🎋 Features

- **Beautiful Haiku Collection**: 25+ original haiku across 5 themes
- **Elegant Design**: Minimalist layout with decorative borders
- **Auto-Refresh**: New haiku every 5 minutes
- **Themed Poetry**: Nature, Technology, Daily Life, Emotions, and Seasons
- **Auto-Start**: Runs automatically when plugged in
- **No Internet Required**: All haiku stored locally

## Part 1: Set up the Raspberry Pi

### 1. Install required system packages:
```bash
sudo apt update
sudo apt install python3-pip python3-pil python3-numpy git
```

### 2. Clone and install the Waveshare library:
```bash
cd ~
git clone https://github.com/waveshareteam/Touch_e-Paper_HAT.git
cd Touch_e-Paper_HAT/python
sudo python3 setup.py install
```

### 3. Install Python packages:
```bash
pip3 install pillow
```

### 4. Create the project directory:
```bash
mkdir ~/haiku-display
cd ~/haiku-display
```

### 5. Copy the display script:
- Copy the `haiku_display.py` script from the artifacts above into this directory

### 6. Copy the Waveshare library:
```bash
cp -r ~/Touch_e-Paper_HAT/python/lib ~/haiku-display/
```

### 7. Test the script:
```bash
cd ~/haiku-display
python3 haiku_display.py
```

You should see a startup message followed by your first haiku!

## Part 2: Auto-start on Boot

### 1. Create the systemd service:
```bash
sudo nano /etc/systemd/system/haiku-display.service
```
Copy the content from the `haiku-display.service` artifact above.

### 2. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable haiku-display.service
sudo systemctl start haiku-display.service
```

### 3. Check the service status:
```bash
sudo systemctl status haiku-display.service
```

### 4. View logs if needed:
```bash
sudo journalctl -u haiku-display.service -f
```

## Part 3: Final Steps

1. **Enable SPI** (required for the eink display):
   ```bash
   sudo raspi-config
   ```
   Go to Interfacing Options → SPI → Enable

2. **Reboot your Pi**:
   ```bash
   sudo reboot
   ```

The haiku display should now start automatically when your Raspberry Pi boots up!

## 🎨 What You'll See

The display features:
- **Clean Header**: "HAIKU" title with decorative dots
- **Three Lines**: Traditional 5-7-5 syllable structure
- **Theme Indicator**: Shows the haiku's theme/season
- **Timestamp**: When the haiku was last updated
- **Elegant Borders**: Double-line frame design

## 📚 Haiku Themes

The system includes haiku from these themes:

### 🌸 Nature
- Spring blossoms and morning dew
- Autumn leaves and harvest moons
- Winter snow and mountain peaks
- Ocean waves and natural rhythms

### 💻 Technology  
- Code and digital rivers
- E-ink displays and pixels
- WiFi connections and modern life
- Binary poetry and screen light

### ☕ Daily Life
- Coffee rituals and morning routines
- Books and reading adventures
- City sounds and office life
- Candles and peaceful moments

### ❤️ Emotions
- Love and heartbeats
- Joy and laughter
- Peace and contemplation
- Dreams and hopes

### 🍂 Seasons
- Spring's first green shoots
- Summer's cicadas and heat
- Autumn's golden harvest
- Winter's frost and artistry

## 🛠️ Customization

### Add Your Own Haiku:
Edit the `HAIKU_THEMES` dictionary in `haiku_display.py`. Follow the format:
```python
{
    "lines": ["First line (5 syllables)", "Second line (7 syllables)", "Third line (5 syllables)"],
    "season": "Your Theme"
}
```

### Change Refresh Interval:
Edit `REFRESH_INTERVAL` in `haiku_display.py` (in seconds):
```python
REFRESH_INTERVAL = 300  # 5 minutes
```

### Modify Design:
Adjust fonts, borders, and layout in the `create_haiku_image()` method.

### Font Customization:
For better typography, install additional fonts:
```bash
sudo apt install fonts-dejavu fonts-liberation fonts-noto
```

## 🔧 Troubleshooting

### Display not working:
- Check SPI is enabled: `lsmod | grep spi`
- Verify wiring matches Waveshare documentation
- Check service logs: `sudo journalctl -u haiku-display.service`

### Service won't start:
- Check file permissions: `chmod +x ~/haiku-display/haiku_display.py`
- Verify paths in service file are correct
- Check Python path: `which python3`

### Font issues:
The script will fall back to default fonts if system fonts aren't available.

## 🎯 Quick Commands

```bash
# Check if service is running
sudo systemctl status haiku-display.service

# Restart the service
sudo systemctl restart haiku-display.service

# Stop the service
sudo systemctl stop haiku-display.service

# View live logs
sudo journalctl -u haiku-display.service -f

# Run manually for testing
cd ~/haiku-display && python3 haiku_display.py
```

## 🌟 Enjoy Your Haiku Display!

Your Raspberry Pi will now display beautiful, contemplative haiku poetry every 5 minutes. Each haiku is carefully crafted to capture moments of beauty, technology, nature, and human experience in the traditional 5-7-5 syllable format.

Perfect for:
- Meditation and mindfulness
- Office decoration
- Gift for poetry lovers
- Learning about haiku
- Adding zen to any space