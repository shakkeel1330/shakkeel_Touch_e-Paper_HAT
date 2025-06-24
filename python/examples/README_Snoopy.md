# Snoopy Touch Animation for Waveshare 2.13" V4 e-Paper Display

This directory contains two fun Snoopy animation programs that respond to touch input on your Waveshare 2.13" V4 Touch e-Paper Display.

## Files

- `snoopy_touch_animation.py` - ASCII art version of Snoopy
- `snoopy_touch_animation_v2.py` - Geometric shapes version (recommended)

## Features

Both programs feature an animated Snoopy character that responds to touch input:

### Touch Areas
- **Top third**: Makes Snoopy dance
- **Middle third**: Makes Snoopy happy
- **Bottom third**: Makes Snoopy sleep (or wake up if already sleeping)

### Animation States
- **Idle**: Snoopy's default state
- **Dancing**: Snoopy moves around with animated arms
- **Happy**: Snoopy shows a happy expression with raised arms
- **Sleeping**: Snoopy closes eyes and shows sleep bubbles
- **Surprised**: Snoopy shows surprise when woken up

## Requirements

- Raspberry Pi Zero 2W (or compatible)
- Waveshare 2.13" V4 Touch e-Paper HAT
- Python 3 with required libraries:
  - PIL (Pillow)
  - RPi.GPIO
  - spidev
  - smbus

## Installation

1. Make sure you have the required libraries installed:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-pil python3-numpy
sudo pip3 install RPi.GPIO spidev
```

2. Ensure your e-paper display is properly connected to the Raspberry Pi.

## Running the Animation

### Option 1: ASCII Art Version
```bash
cd python/examples
sudo python3 snoopy_touch_animation.py
```

### Option 2: Geometric Shapes Version (Recommended)
```bash
cd python/examples
sudo python3 snoopy_touch_animation_v2.py
```

## How It Works

1. The program initializes the e-paper display and touch controller
2. A background thread continuously monitors touch input
3. The main loop updates the animation and refreshes the display
4. Touch events trigger different animation states
5. Each state has a duration and automatically returns to idle

## Display Features

- **Partial Updates**: Uses e-paper partial update for smooth animation
- **Touch Detection**: Real-time touch input processing
- **State Management**: Automatic state transitions with timing
- **Visual Feedback**: Shows current state and touch instructions

## Customization

You can easily modify the animation by:

1. **Adding new states**: Add new animation states to the `SNOOPY_STATES` dictionary
2. **Changing touch areas**: Modify the `get_touch_area()` method
3. **Adjusting timing**: Change `state_duration` values in `handle_touch()`
4. **Adding new graphics**: Create new drawing methods for different poses

## Troubleshooting

- **No touch response**: Check GPIO connections and permissions
- **Display not updating**: Ensure proper SPI configuration
- **Performance issues**: Adjust refresh rate in the main loop

## Exit

Press `Ctrl+C` to exit the animation and clean up resources.

## Notes

- The V2 version uses geometric shapes for better visual quality on e-paper
- The display uses partial updates for smooth animation
- Touch detection runs in a separate thread for responsiveness
- The program automatically handles display sleep and cleanup

Enjoy your interactive Snoopy animation! 🐕 