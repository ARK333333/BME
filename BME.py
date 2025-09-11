from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
import sqlite3
import asyncio
import time
import re

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

client = TelegramClient('mySession', api_id, api_hash)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def animated_dots(text, duration=1.5):
    """Creates animated dots effect"""
    for i in range(int(duration * 4)):
        clear_terminal()
        dots = "." * (i % 4)
        print(f"{text}{dots}")
        time.sleep(0.25)

def parse(message):
    animated_dots("🔍 Analyzing message structure")
    
    clear_terminal()
    print("🔍 Message Analysis Complete!")
    print("=" * 40)
    print("📋 PARSING STEPS:")
    print("  1. Extract title from brackets [ ]")
    print("  2. Parse page numbers")
    print("  3. Extract download link")
    print("=" * 40)
    time.sleep(1)
    
    # Extract title
    clear_terminal()
    print("📝 Step 1: EXTRACTING TITLE...")
    print("🔍 Looking for content between [ ]...")
    time.sleep(0.5)
    
    start = message.find("[") + 1
    end = message.find("]") 
    temp = message[start:end]
    
    if "|" in temp:
        title = temp.replace("|", "")
    else:
        title = temp
    
    clear_terminal()
    print("📝 Step 1: EXTRACTING TITLE... ✅")
    print(f"📖 Found title: '{title}'")
    print("\n📄 Step 2: PROCESSING PAGE NUMBERS...")
    time.sleep(0.8)

    # Parse page numbers
    beginning = temp.split("|")[1].split("-")[0].strip()
    if "صـ" in beginning:
        beginning = int(beginning.replace("صـ", "").strip())
        print(f"📍 Start page: {beginning}")
    elif "بداية الكتاب" in beginning:
        beginning = 0
        print("📍 Start page: Beginning of book")

    last = temp.split("|")[1].split("-")[1].strip()
    if "صـ" in last:
        last = int(last.replace("صـ", "").strip())
        print(f"📍 End page: {last}")
    elif "نهاية الكتاب" in last:
        last = -1
        print("📍 End page: End of book")

    clear_terminal()
    print("📝 Step 1: EXTRACTING TITLE... ✅")
    print(f"📖 Title: '{title}'")
    print("📄 Step 2: PROCESSING PAGE NUMBERS... ✅")
    print(f"📊 Pages: {beginning} → {last}")
    print("\n🔗 Step 3: EXTRACTING DOWNLOAD LINK...")
    time.sleep(0.8)

    # Extract link
    start = message.find("(") + 1
    end = message.find(")") - 1
    link = message[start:end].strip()

    clear_terminal()
    print("🎉 PARSING COMPLETE!")
    print("=" * 50)
    print(f"📖 Title: {title}")
    print(f"📊 Pages: {beginning} → {last}")
    print(f"🔗 Link: {link[:30]}...")
    print("=" * 50)
    time.sleep(1.5)

    downloadable_link = drive_link_to_direct(link)
    download_from_drive(download_link=downloadable_link, filename=temp)
    return {
        "title": title,
        "beginning": beginning,
        "last": last,
        "link": link
    }

def store(title, beginning, end, link):
    animated_dots("💾 Initializing database connection")
    
    # Connect to database
    conn = sqlite3.connect("mydb.sqlite")
    cursor = conn.cursor()

    clear_terminal()
    print("💾 Database Connection... ✅")
    print("🏗️  Setting up database structure...")
    time.sleep(0.5)

    # Create table
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
    print("💾 Database Connection... ✅")
    print("🏗️  Database Structure... ✅") 
    print("📝 Preparing data insertion...")
    time.sleep(0.5)

    # Insert data
    data = (title, beginning, end, link)
    cursor.execute("""
    INSERT INTO courses (title, beginning, end, link)
    VALUES (?, ?, ?, ?)
    """, data)

    clear_terminal()
    print("💾 Database Connection... ✅")
    print("🏗️  Database Structure... ✅")
    print("📝 Data Insertion... ✅")
    print("💾 Saving to disk...")
    time.sleep(0.5)

    # Commit and close
    conn.commit()
    conn.close()

    clear_terminal()
    print("🎊 STORAGE SUCCESSFUL!")
    print("=" * 40)
    print(f"📚 Course: {title}")
    print(f"💾 Saved to: mydb.sqlite") 
    print(f"🆔 Record ID: {cursor.lastrowid}")
    print("=" * 40)
    time.sleep(2)

async def get_message(message):
    clear_terminal()
    print("📨 NEW MESSAGE RECEIVED!")
    print("🔍 Initiating parsing sequence...")
    time.sleep(0.8)
    
    parsed = parse(message)
    return parsed

import requests

def drive_link_to_direct(link: str) -> str:
    clear_terminal()
    print("🔗 Converting Google Drive link...")
    time.sleep(0.5)
    
    # Extract file ID from Google Drive link
    if "drive.google.com" in link:
        if "/file/d/" in link:
            file_id = link.split("/file/d/")[1].split("/")[0]
        elif "id=" in link:
            file_id = link.split("id=")[1].split("&")[0]
        else:
            return link
        
        # Convert to direct download link
        direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        clear_terminal()
        print("🔗 Converting Google Drive link... ✅")
        print(f"📎 Direct download URL created")
        time.sleep(0.5)
        
        return direct_link
    
    return link

def download_from_drive(download_link: str, filename: str):
    clear_terminal()
    print("📥 STARTING DOWNLOAD...")
    print("=" * 40)
    print(f"📂 File: {filename}")
    print(f"🔗 Source: Google Drive")
    print("=" * 40)
    time.sleep(1)
    
    try:
        # Convert to direct download link
        direct_link = drive_link_to_direct(download_link)
        
        clear_terminal()
        print("📥 Downloading file...")
        print(f"📂 {filename}")
        time.sleep(0.5)
        
        # Start download with streaming
        response = requests.get(direct_link, stream=True)
        response.raise_for_status()
        
        # Get file size if available
        total_size = int(response.headers.get('content-length', 0))
        
        clear_terminal()
        print("📥 Download in progress...")
        print(f"📂 {filename}")
        if total_size > 0:
            print(f"📊 Size: {total_size / (1024*1024):.2f} MB")
        time.sleep(0.5)
        
        # Download and save file
        with open(filename, 'wb') as file:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    
                    # Show progress every 1MB
                    if downloaded % (1024*1024) == 0:
                        clear_terminal()
                        print("📥 Download in progress...")
                        print(f"📂 {filename}")
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"📊 Progress: {progress:.1f}%")
                        else:
                            print(f"📊 Downloaded: {downloaded / (1024*1024):.2f} MB")
        
        clear_terminal()
        print("🎉 DOWNLOAD COMPLETE!")
        print("=" * 40)
        print(f"📁 File saved: {filename}")
        print(f"📊 Final size: {os.path.getsize(filename) / (1024*1024):.2f} MB")
        print("=" * 40)
        time.sleep(2)
        os.rename(f"{filename}", f"{filename}.pdf")
        return filename
        
    except requests.exceptions.RequestException as e:
        clear_terminal()
        print("❌ DOWNLOAD FAILED!")
        print(f"🚨 Error: {str(e)}")
        time.sleep(2)
        return None
    except Exception as e:
        clear_terminal()
        print("❌ UNEXPECTED ERROR!")
        print(f"🚨 Error: {str(e)}")
        time.sleep(2)
        return None

def download_file(link: str, title: str) -> str:
    clear_terminal()
    print("🚀 INITIATING DOWNLOAD SEQUENCE...")
    time.sleep(1)
    
    # Create safe filename
    filename = f"{title}"
    
    clear_terminal()
    print("🚀 Download preparation...")
    print(f"📝 Original title: {title}")
    print(f"📂 Filename: {filename}")
    time.sleep(1)
    
    # Download the file
    result = download_from_drive(link, filename)
    
    if result:
        return filename
    else:
        return None

chat = str(os.getenv("CHAT"))
testChat = str(os.getenv("TESTCHAT"))
@client.on(events.NewMessage(chats=testChat))
async def handler(event):
    message_text = event.message.text.lower()
    
    if "drive" in message_text:
        clear_terminal()
        print("🚨 DRIVE LINK DETECTED!")
        print("=" * 50)
        print("🎯 Found: 'drive' in message")
        print(f"💬 From: {event.message.chat.title if event.message.chat else 'Unknown'}")
        print(f"📅 Time: {event.message.date}")
        print("=" * 50)
        time.sleep(1.5)
        
        course = await get_message(event.message.text)
        store(course["title"], course["beginning"], course["last"], course["link"])

        clear_terminal()
        print("✅ MISSION ACCOMPLISHED!")
        print("🔄 Returning to monitoring mode...")
        print("👁️  Watching for new drive links...")
        time.sleep(3)

async def main():
    clear_terminal()
    print("🚀 BME TELEGRAM BOT")
    print("=" * 30)
    time.sleep(0.5)
    
    animated_dots("🔌 Establishing connection to Telegram")
    
    await client.start()
    
    clear_terminal()
    print("🎉 BOT SUCCESSFULLY STARTED!")
    print("=" * 40)
    print("✅ Connected to Telegram API")
    print(f"👥 Monitoring chat: {testChat}")
    print("🎯 Target: Google Drive links")
    print("🔍 Pattern: drive.google.com URLs")
    print("=" * 40)
    print("📡 Bot is now ACTIVE and monitoring...")
    print("💡 Waiting for messages containing drive links...")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        clear_terminal()
        print("🛑 Bot stopped by user")
        print("👋 Goodbye!")