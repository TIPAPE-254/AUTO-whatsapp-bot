import time
import random
import os
import sys
import pyperclip
import google.generativeai as genai
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment
load_dotenv()
CHANNEL_LINK = "https://web.whatsapp.com/channel/0029VanrSXuGE56ckSG6Z03a"
CHANNEL_NAME = "WORLD COMPUTER SCIENCES"

# Load API clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# AI post topics
TOPICS = [
    "Artificial Intelligence",
    "Cybersecurity",
    "Software Engineering",
    "Blockchain",
    "Future of Work",
    "Space Technology",
    "Ethical Hacking",
    "Digital Economy",
    "Robotics",
    "Philosophy of Technology"
]

def generate_post():
    topic = random.choice(TOPICS)

    prompt = f"""
You are the official blogger for a large WhatsApp tech channel called WORLD COMPUTER SCIENCES.

Write a long-form blog post about:
{topic}

STRICT RULES:
- Minimum 300 words (ABSOLUTE)
- Exactly 3 paragraphs
- Each paragraph must be long and detailed
- Professional, futuristic, inspiring
- No emojis
- No hashtags
- Do not shorten
- Do not summarize
- Do not add titles
- Do not ask questions
- Just write the article

If the response is under 300 words, it is considered FAILED.
"""

    # Try OpenAI first
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.8,
            max_tokens=900
        )
        text = response.choices[0].message.content.strip()

        if len(text.split()) < 300:
            raise Exception("Too short, retrying with Gemini")

        return text
    except Exception as e:
        print("OpenAI failed or too short, switching to Gemini:", e)

    # Fallback to Gemini
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        text = response.text.strip()

        if len(text.split()) < 300:
            raise Exception("Gemini too short")

        return text
    except Exception as e:
        print("Gemini failed:", e)

    # Emergency fallback (still long)
    return (
        f"{topic} is one of the most powerful forces shaping the modern world. "
        "Technology is no longer just a tool; it has become the foundation of how societies think, work, trade, and communicate. "
        "From artificial intelligence to global digital networks, every system is being redesigned by computation and data. "
        "Those who understand these systems today are quietly building the structures that will define human life for decades to come.\n\n"
        "Across universities, startups, research labs, and online communities, a new generation of technologists is emerging. "
        "They are not only writing code; they are designing economies, automating decision-making, and redefining what it means to be productive. "
        "In fields like cybersecurity, robotics, and distributed systems, innovation is happening faster than governments can regulate or schools can teach. "
        "This creates a powerful opportunity for learners who take initiative and commit to mastering these tools before they become mainstream.\n\n"
        "The future belongs to those who combine technical skill with vision. "
        "As technology continues to expand into every industry, the demand for people who can build, protect, and optimize digital systems will only grow. "
        "By studying, experimenting, and staying curious, individuals position themselves at the center of this transformation. "
        "This is not just a technological revolution — it is the birth of a new civilization built on knowledge, networks, and intelligent machines."
    )


def remove_emojis(text):
    return text.encode("ascii", "ignore").decode()


def open_group(driver, group_name):
    print("Searching for group:", group_name)

    search_box = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@contenteditable='true' and @data-tab='3']")
        )
    )

    search_box.click()
    time.sleep(1)
    search_box.send_keys(group_name)
    time.sleep(2)

    group = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//span[@title='{group_name}']")
        )
    )

    group.click()
    print("Group opened!")

# Brave / Selenium setup
BRAVE_PATH = "/usr/bin/brave-browser"
PROFILE_PATH = "/home/elvis/.config/BraveBot"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"

options = Options()
options.binary_location = BRAVE_PATH
options.add_argument(f"user-data-dir={PROFILE_PATH}")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# Open WhatsApp Web then channel URL

print("Opening WhatsApp Web...")

# Wait for WhatsApp Web to load
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, '//div[@id="app"]'))
)
print("WhatsApp loaded!")

# Open group by name
open_group(driver, CHANNEL_NAME)
time.sleep(5)

# Wait for post UI
post_box = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located(
        (By.XPATH, "//div[@contenteditable='true' and @data-tab='10']")
    )
)

# If run with --once, post once and exit (useful for schedulers)
if "--once" in sys.argv or os.getenv("RUN_ONCE") == "1":
    post = generate_post()
    post = remove_emojis(post)
    print("Posting once:\n", post)

    post_box.click()
    post_box.send_keys(post)
    time.sleep(1)
    post_box.send_keys(Keys.ENTER)

    print("Posted once; quitting.")
    time.sleep(2)
    driver.quit()
    sys.exit(0)

# Auto-post loop: generate, post, wait, repeat
while True:
    post = generate_post()
    print("Posting:\n", post)

    post_box.send_keys(post)
    time.sleep(1)
    post_box.send_keys(Keys.ENTER)

    time.sleep(1800)  # wait 30 minutes before next post
