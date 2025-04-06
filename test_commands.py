from agent import BrowserAgent
from dotenv import load_dotenv

load_dotenv()

agent = BrowserAgent(headless=False)

try:
    print("\n=== TEST 1: HARDCODED ACTIONS ===")
    agent.navigate("https://google.com")
    agent.type_text("textarea[name='q']", "playwright automation")
    agent.press_key("Enter")

    print("\n=== TEST 2: GENERATED ACTIONS ===")
    print(agent.interact("Search for Gemini API on Google"))

finally:
    agent.close()