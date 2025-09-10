from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
import sqlite3
import asyncio

load_dotenv()

api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

client = TelegramClient('mySession', api_id, api_hash)

def parse(message):
    start = message.find("[") + 1
    end = message.find("]") 
    temp = message[start:end]
    
    title = temp.split("|")[0].strip()

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

    start = message.find("(") + 1
    end = message.find(")") - 1
    link = message[start:end].strip()

    return {
        "title":title,
        "beginning":beginning,
        "last":last,
        "link":link
    }

def store(title, beginning, end, link):
    # 1. Connect (creates file if it doesn't exist)
    conn = sqlite3.connect("mydb.sqlite")
    cursor = conn.cursor()

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

    # 3. Insert data
    data = (title, beginning, end, link)
    cursor.execute("""
    INSERT INTO courses (title, beginning, end, link)
    VALUES (?, ?, ?, ?)
    """, data)

    # 4. Commit + close
    conn.commit()
    conn.close()

async def get_messages(client, limit, link):
    courses_list = []  # Store parsed messages
    async for message in client.iter_messages(link, limit, search='drive'):
        if message.text:  # Check if message has text
            parsed = parse(message.text)
            courses_list.append(parsed)
    return courses_list  # Return the list

chat = str(os.getenv("CHAT"))
testChat = str(os.getenv("TESTCHAT"))
@client.on(events.NewMessage(chats=testChat, pattern='.*drive.*'))
async def handler(event):
    print("new message found: ", event.message.text)
    #messages = await client.get_messages(chat, 5, search="drive")
    #print(messages.stringify())
    courses = await get_messages(client, 1, testChat)
    for course in courses:
        store(course["title"], course["beginning"], course["last"], course["link"])

async def main():
    # Now you can use all client methods listed below, like for example...
    await client.start()
    await client.run_until_disconnected()
    
# with client:
#     client.loop.run_until_complete(main())

if __name__ == '__main__':
    asyncio.run(main())