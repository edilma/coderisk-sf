from dotenv import load_dotenv
import os

load_dotenv()  # loads .env into environment
api_key = os.getenv("VISION_AGENT_API_KEY")

print("ADE key loaded:", bool(api_key))  # should print True
