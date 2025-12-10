"""
QuickAPI UI Components - Block UI-like interface for QuickAPI

This module provides Block UI-style UI components that integrate with QuickAPI's
template system, allowing for easy creation of interactive web interfaces.
"""

from .components import (
    # Form components
    Textbox, Slider, Number, Checkbox, Radio, Dropdown, 
    Image, Audio, Video, File,
    
    # Display components
    Label, Text, HTML, Markdown, JSON, Gallery,
    
    # Layout components
    Row, Column, Tabs, Tab, Group, Accordion,
    
    # Interactive components
    Button, Chatbot, Plot
)

from .interface import Interface
from .blocks import Blocks

__all__ = [
    # Form components
    "Textbox", "Slider", "Number", "Checkbox", "Radio", "Dropdown",
    "Image", "Audio", "Video", "File",
    
    # Display components
    "Label", "Text", "HTML", "Markdown", "JSON", "Gallery",
    
    # Layout components
    "Row", "Column", "Tabs", "Tab", "Group", "Accordion",
    
    # Interactive components
    "Button", "Chatbot", "Plot",
    
    # Main classes
    "Interface", "Blocks"
]