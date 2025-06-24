#!/usr/bin/env python3
"""
Simple Real-time Display Launcher for Waveshare 2.9 inch e-Paper
This script runs the real-time display that updates every second
"""

import sys
import os

# Add the lib directory to the path
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

try:
    from TP_lib.simple_realtime import run_display
    print("Starting Real-time Display...")
    run_display()
except ImportError as e:
    print(f"Import Error: {e}")
    print("Make sure you're running this from the python directory")
    print("and all dependencies are installed:")
    print("sudo pip3 install requests psutil")
except Exception as e:
    print(f"Error: {e}")
    print("Make sure the e-Paper display is properly connected") 