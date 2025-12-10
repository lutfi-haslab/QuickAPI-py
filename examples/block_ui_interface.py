"""
Example of using QuickAPI's Block UI Interface

This example demonstrates how to create a simple interface using QuickAPI's
Block UI UI components.
"""

import sys
import os

# Add the parent directory to the path so we can import quickapi
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quickapi.ui import Interface, Textbox, Slider, Text, Label


def greet(name, intensity):
    """Simple greeting function"""
    return "Hello, " + name + "!" * int(intensity)


def sentiment_analyzer(text):
    """Simple sentiment analysis function"""
    if any(word in text.lower() for word in ["good", "love", "happy", "nice"]):
        return "😊 Positive"
    elif any(word in text.lower() for word in ["bad", "sad", "hate"]):
        return "😢 Negative"
    return "😐 Neutral"


def create_simple_interface():
    """Create a simple interface with the greet function"""
    demo = Interface(
        fn=greet,
        inputs=[Textbox(label="Name"), Slider(label="Intensity", minimum=1, maximum=10)],
        outputs=[Text(label="Output")],
        title="Simple Greeting Interface hahah",
        description="Enter your name and intensity to generate a greeting.",
        api_name="greet"
    )
    
    return demo


def create_sentiment_interface():
    """Create a sentiment analysis interface"""
    demo = Interface(
        fn=sentiment_analyzer,
        inputs=Textbox(label="Type a sentence"),
        outputs=Label(label="Sentiment Result"),
        title="Simple Sentiment Analyzer",
        description="Enter a sentence to analyze its sentiment.",
        api_name="sentiment"
    )
    
    return demo


if __name__ == "__main__":
    # Choose which interface to run
    import argparse
    
    parser = argparse.ArgumentParser(description="QuickAPI Block UI-like Interface Example")
    parser.add_argument(
        "--type", 
        choices=["greet", "sentiment"], 
        default="greet",
        help="Type of interface to run"
    )
    
    args = parser.parse_args()
    
    if args.type == "greet":
        demo = create_simple_interface()
        print("🚀 Simple Greeting Interface")
    else:
        demo = create_sentiment_interface()
        print("🚀 Simple Sentiment Analyzer")
    
    print("🌐 Open: http://127.0.0.1:8000")
    
    # Launch the interface
    demo.launch(server_port=8000)