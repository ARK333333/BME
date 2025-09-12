from telethon import TelegramClient, events
import os

def add_chapter(text: str, folder_name: str, chapter_name: str) -> None:
    import requests
    
    print(f"DEBUG: Starting add_chapter with text: {text[:50]}...")
    
    direct_link = f"https://drive.google.com/uc?export=download&id={text[text.find('(') + 1:text.find(')') - 1].strip().split('/file/d/')[1].split('/')[0] if '/file/d/' in text[text.find('(') + 1:text.find(')') - 1].strip() else text[text.find('(') + 1:text.find(')') - 1].strip().split('id=')[1].split('&')[0]}"
    print(f"DEBUG: Direct link created: {direct_link}")
    
    response = requests.get(direct_link, stream=True)
    response.raise_for_status()
    print(f"DEBUG: HTTP response status: {response.status_code}")

    # Download and save file
    file_name = text[text.find("[") + 1 : text.find("]")].replace("|", "")
    print(f"DEBUG: file_name extracted: {file_name}")
    
    with open(f"{folder_name if not os.path.isdir(f'{folder_name}/more') else f'{folder_name}/more'}/{file_name}", 'wb') as file:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                downloaded += len(chunk)
    os.rename(f"{folder_name}/{file_name}", f"{folder_name}/{file_name}.pdf") if not os.path.isdir(f"{folder_name}/more") else os.rename(f"{folder_name}/more/{file_name}", f"{folder_name}/more/{file_name}.pdf") 
    print(f"DEBUG: Downloaded {downloaded} bytes")

    if not os.path.isdir(f"{folder_name}/more"):
        os.mkdir(f"{folder_name}/more")
        return 
    
    # merge file
    from PyPDF2 import PdfMerger
    beginning_of_chapter_name = int(chapter_name.split("-")[0].replace("صـ","").strip()) if "بداية الكتاب" not in chapter_name else 1
    beginning_of_merged_pdfs_name = int(sorted(os.listdir(f'{folder_name}'))[-1].split("-")[0][sorted(os.listdir(f'{folder_name}'))[-1].split("-")[0].find("صـ") + 2:].replace(".pdf","").strip()) if not ("بداية الكتاب" in sorted(os.listdir(f'{folder_name}'))[-1]) else 1
    if  beginning_of_chapter_name < beginning_of_merged_pdfs_name:
        merger = PdfMerger()
        merger.append(f"{folder_name}/more/{file_name}.pdf")
        merger.append(f"{folder_name}/{sorted(os.listdir(f'{folder_name}'))[-1]}")
        merger.write(f"{folder_name}/{sorted(os.listdir(f'{folder_name}'))[-1]}")
        merger.close()
        os.rename(f"{folder_name}/{sorted(os.listdir(f'{folder_name}'))[-1]}", f"{folder_name}/{sorted(os.listdir(f'{folder_name}'))[-1]}".replace(f"{beginning_of_merged_pdfs_name}", f"{beginning_of_chapter_name}")) 
    end_of_chapter_name = int(chapter_name.split("-")[1].replace("صـ","").strip()) if "نهاية الكتاب" not in chapter_name else 99999999999
    end_of_merged_pdfs_name = int(sorted(os.listdir(f'{folder_name}'))[-1].split("-")[1][sorted(os.listdir(f'{folder_name}'))[-1].split("-")[1].find("صـ") + 2:].replace(".pdf","").strip()) if not ("نهاية الكتاب" in sorted(os.listdir(f'{folder_name}'))[-1]) else 999999999
    if  end_of_chapter_name > end_of_merged_pdfs_name:
        merger = PdfMerger()
        merger.append(f"{folder_name}/{sorted(os.listdir(f'{folder_name}'))[-1]}")
        merger.append(f"{folder_name}/more/{file_name}.pdf")
        merger.write(f"{folder_name}/{sorted(os.listdir(f'{folder_name}'))[-1]}")
        merger.close()
        os.rename(f"{folder_name}/{sorted(os.listdir(f'{folder_name}'))[-1]}", f"{folder_name}/{sorted(os.listdir(f'{folder_name}'))[-1]}".replace(f"{end_of_merged_pdfs_name}", f"{end_of_chapter_name}")) 

async def main() -> None:
    from dotenv import load_dotenv
    load_dotenv()

    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    print(f"DEBUG: API credentials loaded")
    
    client = TelegramClient('mySession', api_id, api_hash)

    await client.start()
    print(f"DEBUG: Telegram client started")
    
    chatName = str(os.getenv("TESTCHAT"))
    print(f"DEBUG: Monitoring chat: {chatName}")
    
    @client.on(events.NewMessage(chats=chatName))
    async def handler(event):
        print(f"DEBUG: New message received")
        print(f"DEBUG: Message text: {event.message.text[:100]}...")
        
        book_name = event.message.text.split("|")[0][event.message.text.split("|")[0].find("[") + 1:]
        chapter_name = event.message.text.split("|")[1][:event.message.text.split("|")[1].find("(") - 1]
        print(f"DEBUG: Book name: {book_name}")
        print(f"DEBUG: Chapter name: {chapter_name}")
        
        if "drive" in event.message.text:
            print(f"DEBUG: 'drive' found in message")
            if not os.path.isdir(f"{book_name}"):
                os.mkdir(book_name)
                print(f"DEBUG: Created directory: {book_name}")
            if not os.path.isdir(f"{book_name}/{chapter_name}"):
                print(f"DEBUG: Calling add_chapter function")
                add_chapter(text=event.message.text, folder_name=book_name, chapter_name=chapter_name)
        else:
            print(f"DEBUG: No 'drive' found in message")

    await client.run_until_disconnected()

import asyncio
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
        print("👋 Goodbye!")