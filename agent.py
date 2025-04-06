from playwright.sync_api import sync_playwright
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class BrowserAgent:
    def __init__(self, headless=False):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page()

    def navigate(self, url):
        self.page.goto(url, wait_until="domcontentloaded")
        print(f"🌐 Navigated to: {url}")
        self.page.wait_for_timeout(5000)

    def click(self, selector):
        self.page.wait_for_selector(selector, state="visible", timeout=10000)
        self.page.click(selector)
        print(f"🖱️ Clicked: {selector}")
        self.page.wait_for_timeout(5000)

    def type_text(self, selector, text):
        self.page.wait_for_selector(selector, state="visible", timeout=10000)
        self.page.fill(selector, text)
        print(f"⌨️ Typed '{text}' in: {selector}")
        self.page.wait_for_timeout(5000)

    def press_key(self, key):
        self.page.keyboard.press(key)
        print(f"🔘 Pressed key: {key}")
        self.page.wait_for_timeout(5000)

    def _generate_actions(self, command: str) -> list:
        print(f"\n💬 Original Command: {command}")
        prompt = f"""Convert this command to browser actions: "{command}".
        Use STRICT JSON format with these REQUIRED fields:
        - navigate(url): Must include full URL
        - click(selector): Use VISIBLE elements with CSS selectors
        - type(selector, text): Precise input fields
        - press(key): Keyboard keys only

        Example response:
        [{{"action":"navigate","url":"https://google.com"}},
         {{"action":"type","selector":"textarea[name='q']","text":"cats"}},
         {{"action":"press","key":"Enter"}}]"""
        
        try:
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                params={"key": os.getenv("GEMINI_API_KEY")},
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts":[{"text": prompt}]}]}
            )
            response.raise_for_status()
            generated_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            print("🔧 Raw Gemini Response:", generated_text)  # Debug
            return json.loads(generated_text)
        except Exception as e:
            print(f"🔴 API Error: {str(e)}")
            print(f"🔴 Full Response: {response.text if 'response' in locals() else ''}")
            return []

    def interact(self, command: str) -> str:
        try:
            actions = self._generate_actions(command)
            if not actions:
                return "Error: No actions generated"
                
            print("\n🚀 Executing Actions:")
            for action in actions:
                print(f"⚡ Action: {action}")
                getattr(self, action["action"])(**{k:v for k,v in action.items() if k != "action"})
            return "Success"
        except Exception as e:
            return f"Error: {str(e)}"

    def close(self):
        self.browser.close()
        self.playwright.stop()