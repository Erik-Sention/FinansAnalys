"""
Finansiell Dashboard - Entry point för deployment
"""
import sys
import os

# Add current directory to Python path for deployment compatibility
try:
    # When running as a script, __file__ is available
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # When running with exec() or in some deployment contexts
    current_dir = os.getcwd()

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
from dashboard import main

if __name__ == "__main__":
    main()
