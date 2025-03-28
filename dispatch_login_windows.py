import asyncio
import os
import sys
import platform

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

# Import the necessary modules
from browser_use import Agent, Browser, BrowserConfig

# Load environment variables
load_dotenv()

# Get login credentials from environment variables
EMAIL = os.getenv('DISPATCH_EMAIL')
PASSWORD = os.getenv('DISPATCH_PASSWORD')

# Check if credentials are set
if not EMAIL or not PASSWORD:
    raise ValueError('DISPATCH_EMAIL and DISPATCH_PASSWORD must be set in the .env file')

# Monkey patch the SignalHandler class to work on Windows
# This is done before importing the Agent class
if platform.system() == 'Windows':
    from browser_use.utils import SignalHandler
    
    # Save the original register method
    original_register = SignalHandler.register
    
    # Create a new register method that does nothing on Windows
    def windows_register(self):
        print("Signal handling disabled on Windows")
        pass
    
    # Replace the register method
    SignalHandler.register = windows_register

async def main():
    """Main function to execute the login automation."""
    # Define the task with detailed instructions
    task = (
        "Go to https://app.dispatchit.com/users/sign_in. "
        f"Login with email {EMAIL} and password {PASSWORD}. "
        "After logging in, look for an 'accept' button on the page and click it if it exists. "
        "If there's no 'accept' button, just confirm that you've successfully logged in."
    )
    
    # Initialize the language model
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError('OPENAI_API_KEY is not set. Please add it to your .env file or environment variables.')
    
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
        api_key=SecretStr(os.getenv('OPENAI_API_KEY', ''))
    )
    
    # Configure browser settings and create browser instance
    browser_config = BrowserConfig(
        headless=False,  # Set to False to see the browser in action
        browser_type="chromium",  # Explicitly set browser type
    )
    browser = Browser(config=browser_config)
    
    try:
        # Create the agent with the browser instance
        agent = Agent(
            task=task, 
            llm=model, 
            browser=browser,
            use_vision=True
        )
        
        # Run the agent with a reasonable step limit
        await agent.run(max_steps=15)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Make sure to close the browser when done
        await browser.close()
    
    print("Login automation completed.")

if __name__ == "__main__":
    asyncio.run(main())
