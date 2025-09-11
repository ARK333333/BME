
from telethon import TelegramClient, events
import os

def add_chapter(text):
    import requests

    direct_link = f"https://drive.google.com/uc?export=download&id={text[text.find('(') + 1:text.find(')') - 1].strip().split('/file/d/')[1].split('/')[0] if '/file/d/' in text[text.find('(') + 1:text.find(')') - 1].strip() else text[text.find('(') + 1:text.find(')') - 1].strip().split('id=')[1].split('&')[0]}"
    response = requests.get(direct_link, stream=True)
    response.raise_for_status()

    # Download and save file
    filename = text[text.find("[") + 1 : text.find("]")].replace("|", "")
    with open(filename, 'wb') as file:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                downloaded += len(chunk)
    os.rename(f"{filename}", f"{filename}.pdf")

    # merge file
        

async def main():
    from dotenv import load_dotenv
    load_dotenv()

    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    client = TelegramClient('mySession', api_id, api_hash)

    await client.start()
    await client.run_until_disconnected()

    chatName = str(os.getenv("TESTCHAT"))
    @client.on(events.NewMessage(chats=chatName))
    async def handler(event):
        book_name = event.message.text.split("|")[0]
        chapter_name = event.message.text.split("|")[1][:event.message.text.split("|")[1].find("(")]
        if "drive" in event.message.text:
            if not os.path.isdir(f"{book_name}"):
                os.mkdir(book_name)
            if not os.path.isdir(f"{book_name}/{chapter_name}"):
                add_chapter(event.message.text)

import asyncio
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
        print("👋 Goodbye!")