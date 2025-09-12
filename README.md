# BME Telegram Bot

A Python bot that automatically monitors Telegram channels for Google Drive links containing educational materials, downloads PDF files, and organizes them by merging chapters when needed.

## Features
- 📱 Monitors specified Telegram channels for Drive links
- 📁 Automatically creates organized folder structure
- 📄 Downloads PDF files from Google Drive
- 🔗 Merges PDF chapters intelligently based on page ranges
- 🎯 Parses Arabic text for book titles and page numbers
- 💾 Handles file naming with Arabic characters

## Technologies Used
- Python 3.8+
- Telethon (Telegram API)
- PyPDF2 (PDF manipulation)
- Requests (HTTP downloads)
- python-dotenv (Environment variables)
