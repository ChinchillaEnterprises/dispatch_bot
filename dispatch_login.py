import asyncio
import os
import sys
import platform

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from browser_use import Agent, Browser, BrowserConfig

# Load environment variables
load_dotenv()

# Define login credentials
class DispatchCredentials:
    EMAIL = "mehrad@chinchilla-ai.com"
    PASSWORD = "Mehrad1995bayat!"

async def main():
    """Main function to execute the login automation."""
    # Define the task with detailed instructions
    task = (
        "Go to https://app.dispatchit.com/users/sign_in. "
        f"Login with email {DispatchCredentials.EMAIL} and password {DispatchCredentials.PASSWORD}. "
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
    except NotImplementedError as e:
        if "add_signal_handler" in str(e):
            print("Warning: Signal handling not supported on Windows. Continuing without it.")
            # You might need to implement a Windows-specific solution here
        else:
            raise
    finally:
        # Make sure to close the browser when done
        await browser.close()
    
    print("Login automation completed.")

if __name__ == "__main__":
    asyncio.run(main())
