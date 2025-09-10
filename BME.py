from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
import sqlite3
import asyncio
import time

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

client = TelegramClient('mySession', api_id, api_hash)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def parse(message):
    clear_terminal()
    print("🔍 Parsing message...")
    
    
    start = message.find("[") + 1
    end = message.find("]") 
    temp = message[start:end]
    
    clear_terminal()
    print("🔍 Parsing message...")
    print("📝 Extracting title...")
    
    
    title = temp.split("|")[0].strip()

    clear_terminal()
    print("🔍 Parsing message...")
    print("📝 Extracting title... ✅")
    print("📄 Processing page numbers...")
    

    beginning = temp.split("|")[1].split("-")[0]
    if "صـ" in beginning:
        beginning = int(beginning.replace("صـ", "").strip())
    elif "بداية الكتاب" in beginning:
        beginning = 0

    last = temp.split("|")[1].split("-")[1]
    if "صـ" in last:
        last = int(last.replace("صـ", "").strip())
    elif "نهاية الكتاب" in last:
        last = -1

    clear_terminal()
    print("🔍 Parsing message...")
    print("📝 Extracting title... ✅")
    print("📄 Processing page numbers... ✅")
    print("🔗 Extracting link...")
    

    start = message.find("(") + 1
    end = message.find(")") - 1
    link = message[start:end].strip()

    clear_terminal()
    print("🔍 Parsing message...")
    print("📝 Extracting title... ✅")
    print("📄 Processing page numbers... ✅")
    print("🔗 Extracting link... ✅")
    print(f"✨ Parsed: {title} (Pages {beginning}-{last})")
    

    return {
        "title":title,
        "beginning":beginning,
        "last":last,
        "link":link
    }

def store(title, beginning, end, link):
    clear_terminal()
    print("💾 Connecting to database...")
    
    
    # 1. Connect (creates file if it doesn't exist)
    conn = sqlite3.connect("mydb.sqlite")
    cursor = conn.cursor()

    clear_terminal()
    print("💾 Connecting to database... ✅")
    print("🏗️  Creating table if needed...")
    

    # 2. Create table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        beginning INTEGER,
        end INTEGER,
        link TEXT
    )
    """)

    clear_terminal()
    print("💾 Connecting to database... ✅")
    print("🏗️  Creating table if needed... ✅")
    print("📥 Inserting data...")
    

    # 3. Insert data
    data = (title, beginning, end, link)
    cursor.execute("""
    INSERT INTO courses (title, beginning, end, link)
    VALUES (?, ?, ?, ?)
    """, data)

    clear_terminal()
    print("💾 Connecting to database... ✅")
    print("🏗️  Creating table if needed... ✅")
    print("📥 Inserting data... ✅")
    print("💾 Saving changes...")
    

    # 4. Commit + close
    conn.commit()
    conn.close()

    clear_terminal()
    print("💾 Connecting to database... ✅")
    print("🏗️  Creating table if needed... ✅")
    print("📥 Inserting data... ✅")
    print("💾 Saving changes... ✅")
    print(f"🎉 Successfully stored: {title}")
    

async def get_message(message):
    clear_terminal()
    print("📨 Processing new message...")
    
    
    parsed = parse(message)
    return parsed

chat = str(os.getenv("CHAT"))
testChat = str(os.getenv("TESTCHAT"))

@client.on(events.NewMessage(chats=testChat))
async def handler(event):
    clear_terminal()
    print("🚨 NEW MESSAGE DETECTED!")
    print("🔍 Contains 'drive' keyword")
    print(f"📝 Message: {event.message.text[:50]}...")
    
    if ("drive" in event.message.text):
        course = await get_message(event.message.text)
        store(course["title"], course["beginning"], course["last"], course["link"])
    
    clear_terminal()
    print("✅ MESSAGE PROCESSED SUCCESSFULLY!")
    print("👀 Listening for new messages...")

async def main():
    clear_terminal()
    print("🚀 Starting Telegram Bot...")
    
    
    clear_terminal()
    print("🚀 Starting Telegram Bot...")
    print("🔌 Connecting to Telegram...")
    
    await client.start()
    
    clear_terminal()
    print("🚀 Starting Telegram Bot... ✅")
    print("🔌 Connected to Telegram... ✅")
    print("👀 Listening for messages with 'drive'...")
    print("📡 Bot is now active and waiting...")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())

