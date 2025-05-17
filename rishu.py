import re
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from pyrogram.enums import ChatAction
from pyrogram.errors import UserNotParticipant
import requests
import time
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import pymongo
from typing import Optional
import random

# Bot details from environment variables
BOT_TOKEN = "6956731651:AAE9I-6IYMmLWSXgDQhfRog6lFfLBJEK8bs"
CHANNEL_1_USERNAME = "Rishucoder"  # First channel username
CHANNEL_2_USERNAME = "Rishu_mood"  # Second channel username
API_HASH = "42a60d9c657b106370c79bb0a8ac560c"
API_ID = "14050586"
TERABOX_API = "https://terabox-player.rishuapi.workers.dev/?url="
DUMP_CHANNEL = "-1002561334306"
ADMIN_ID = int(os.getenv("ADMIN_ID", "5738579437"))  # Admin ID for new user notifications

# Flask app for monitoring
flask_app = Flask(__name__)
start_time = time.time()

# MongoDB setup
mongo_client = pymongo.MongoClient(
    os.getenv(
        "MONGO_URI",
        "mongodb+srv://Teraboxdownloader:Rajubhai@cluster0.tbocw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )
)
db = mongo_client[os.getenv("MONGO_DB_NAME", "Rishu-free-db")]
users_collection = db[os.getenv("MONGO_COLLECTION_NAME", "users")]

# Pyrogram bot client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@flask_app.route('/')
def home():
    uptime_minutes = (time.time() - start_time) / 60
    user_count = users_collection.count_documents({})
    return f"Bot uptime: {uptime_minutes:.2f} minutes\nUnique users: {user_count}"


async def is_user_in_channel(client, user_id, channel_username):
    """Check if the user is a member of the specified channel."""
    try:
        await client.get_chat_member(channel_username, user_id)
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return False


async def send_join_prompt(client, chat_id):
    """Send a message asking the user to join both channels."""
    join_button_1 = InlineKeyboardButton("♡ Join ♡", url=f"https://t.me/{CHANNEL_1_USERNAME}")
    join_button_2 = InlineKeyboardButton("♡ Join ♡", url=f"https://t.me/{CHANNEL_2_USERNAME}")
    markup = InlineKeyboardMarkup([[join_button_1], [join_button_2]])
    await client.send_message(
        chat_id,
        "♡ You need to join both channels to use this bot.. ♡",
        reply_markup=markup,
    )


@app.on_message(filters.command("start"))
async def start_message(client, message):
    user_id = message.from_user.id
    # Check if the user is new
    if users_collection.count_documents({'user_id': user_id}) == 0:
        # Insert new user into the database
        users_collection.insert_one({'user_id': user_id})

        # Notify the admin about the new user
        await client.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"💡 **New User Alert**:\n\n"
                f"👤 **User:** {message.from_user.mention}\n"
                f"🆔 **User ID:** `{user_id}`\n"
                f"📊 **Total Users:** {users_collection.count_documents({})}"
            )
        )

    # Random image selection
    image_urls = [
        "https://graph.org/file/f76fd86d1936d45a63c64.jpg",
        "https://graph.org/file/69ba894371860cd22d92e.jpg",
        "https://graph.org/file/67fde88d8c3aa8327d363.jpg",
        "https://graph.org/file/3a400f1f32fc381913061.jpg",
        "https://graph.org/file/a0893f3a1e6777f6de821.jpg",
        "https://graph.org/file/5a285fc0124657c7b7a0b.jpg",
        "https://graph.org/file/25e215c4602b241b66829.jpg",
        "https://graph.org/file/a13e9733afdad69720d67.jpg",
        "https://graph.org/file/692e89f8fe20554e7a139.jpg",
        "https://graph.org/file/db277a7810a3f65d92f22.jpg",
        "https://graph.org/file/a00f89c5aa75735896e0f.jpg",
        "https://graph.org/file/f86b71018196c5cfe7344.jpg",
        "https://graph.org/file/a3db9af88f25bb1b99325.jpg",
        "https://graph.org/file/5b344a55f3d5199b63fa5.jpg",
        "https://graph.org/file/84de4b440300297a8ecb3.jpg",
        "https://graph.org/file/84e84ff778b045879d24f.jpg",
        "https://graph.org/file/a4a8f0e5c0e6b18249ffc.jpg",
        "https://graph.org/file/ed92cada78099c9c3a4f7.jpg",
        "https://graph.org/file/d6360613d0fa7a9d2f90b.jpg",
        "https://graph.org/file/37248e7bdff70c662a702.jpg",
        "https://graph.org/file/0bfe29d15e918917d1305.jpg",
        "https://graph.org/file/16b1a2828cc507f8048bd.jpg",
        "https://graph.org/file/e6b01f23f2871e128dad8.jpg",
        "https://graph.org/file/cacbdddee77784d9ed2b7.jpg",
        "https://graph.org/file/ddc5d6ec1c33276507b19.jpg",
        "https://graph.org/file/39d7277189360d2c85b62.jpg",
        "https://graph.org/file/5846b9214eaf12c3ed100.jpg",
        "https://graph.org/file/ad4f9beb4d526e6615e18.jpg",
        "https://graph.org/file/3514efaabe774e4f181f2.jpg"
    ]
    random_image = random.choice(image_urls)
    
    # Inline buttons for channel join
    join_button_1 = InlineKeyboardButton("♡ Support ♡", url=f"https://t.me/Ur_rishu_143")
    join_button_2 = InlineKeyboardButton("♡ All Bots ♡", url=f"https://t.me/vip_robotz")
    support_button = InlineKeyboardButton('♡ Support ♡', url='https://t.me/Ur_support07')

    markup = InlineKeyboardMarkup([[join_button_1], [join_button_2], [support_button]])


    # Send the welcome message with the random image
    await client.send_photo(
        chat_id=message.chat.id,
        photo=random_image,
        caption=f"""**┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼──────•
┆◍ ʜᴇʏ {message.from_user.mention} !
└──────────────────────•
» ✦ ϻσsᴛ ᴘσᴡєꝛғυʟʟ ᴛєꝛᴧʙσx ʙσᴛ  
» ✦ ʙєsᴛ ғєᴧᴛυꝛє ʙσᴛ ση ᴛєʟєɢꝛᴧϻ 
» ✦ ғᴧsᴛ ᴅσᴡηʟσᴧᴅ sυᴘᴘσꝛᴛєᴅ
» ✦ ησ ʟᴧɢ, ғᴧsᴛ ᴧηᴅ sєᴄυꝛє 
» ✦ ᴘꝛєϻɪυϻ ғєᴧᴛυꝛєs
•──────────────────────•
❖ 𝐏ᴏᴡᴇʀᴇᴅ ʙʏ  »»  [˹ʀɪsʜυ ʙσᴛ˼ ](t.me/ur_rishu_143) 
•──────────────────────•**""",
        reply_markup=markup
    )


@app.on_message(filters.command("Rishu"))
async def status_message(client, message):
    user_count = users_collection.count_documents({})
    uptime_minutes = (time.time() - start_time) / 60
    await message.reply_text(f"💫 Bot uptime: {uptime_minutes:.2f} minutes\n\n👥 Total unique users: {user_count}")


@app.on_message(filters.text & ~filters.command(["start", "status"]))
async def get_video_links(client, message):
    user_id = message.from_user.id

    # Check if the user is a member of both channels
    if not await is_user_in_channel(client, user_id, CHANNEL_1_USERNAME):
        await send_join_prompt(client, message.chat.id)
        return
    if not await is_user_in_channel(client, user_id, CHANNEL_2_USERNAME):
        await send_join_prompt(client, message.chat.id)
        return

    # Process the video request
    await process_video_request(client, message)


def fetch_video_details(video_url: str) -> Optional[str]:
    """Fetch video thumbnail from a direct TeraBox URL."""
    try:
        response = requests.get(video_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find("meta", property="og:image")["content"] if soup.find("meta", property="og:image") else None
    except requests.exceptions.RequestException:
        return None


def extract_terabox_id(url: str) -> Optional[str]:
    match = re.search(r'/s/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else None



async def process_video_request(client, message):
    video_url = message.text.strip()
    await message.reply_chat_action(ChatAction.TYPING)

    try:
        # Call the API
        api_url = f"https://teraboxdown.rishuapi.workers.dev/?url={video_url}"
        response = requests.get(api_url).json()

        # Extract details
        file_name = response.get("file_name", "Unknown")
        file_size = response.get("size", "Unknown")
        download_url = response.get("link")
        thumbnail = response.get("thumbnail") or fetch_video_details(video_url) or "https://envs.sh/L75.jpg"

        # Main player
        main_player_url = f"{TERABOX_API}{video_url}"
        web_app_1 = WebAppInfo(url=main_player_url)

    # Second player using extracted ID
        terabox_id = extract_terabox_id(video_url)
        if terabox_id:
            second_player_url = f"https://areshai35.brendanav492.workers.dev/?id={terabox_id}"
            web_app_2 = WebAppInfo(url=second_player_url)
        else:
            web_app_2 = None
        # Inline buttons
        buttons = [
            [InlineKeyboardButton("♡ PLAY VIDEO 1 ♡", web_app=web_app_2)],
        ]
        if web_app_2:
            buttons.append([InlineKeyboardButton("♡ PLAY VIDEO 2 ♡", web_app=web_app_1)])
        
        buttons.append([InlineKeyboardButton("♡ SUPPORT ♡", url='https://t.me/Ur_rishu_143')])
        buttons.append([InlineKeyboardButton("♡ All bots ♡", url='https://t.me/vip_robotz')])

        markup = InlineKeyboardMarkup(buttons)

        # Caption for user
        caption = (
            f"**Dear: 🤩 {message.from_user.mention}\n\n"
            f"📦 File Name: `{file_name}`\n\n"
            f"📁 Size: `{file_size}`\n"
            f"💡 Download Here [Link]({download_url})**\n\n"
            f"💾Here's your video:**"
        )

        await client.send_photo(
            chat_id=message.chat.id,
            photo=thumbnail,
            caption=caption,
            reply_markup=markup,
            has_spoiler=True
        )

        # Dump caption
        dump_caption = (
            f"From {message.from_user.mention}:\n"
            f"File: `{file_name}`\n"
            f"Size: `{file_size}`\n"
            f"Play video: [Player]({second_player_url})\n"
            f"Play video: [Player 2]({main_player_url})\n"
            f"Download Video: [Download Link]({download_url})"
        )

        await client.send_photo(
            chat_id=DUMP_CHANNEL,
            photo=thumbnail,
            caption=dump_caption
        )

    except requests.exceptions.RequestException as e:
        await message.reply_text(f"Error connecting to the API: {str(e)}")
# Flask thread for monitoring
def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)


flask_thread = Thread(target=run_flask)
flask_thread.start()

# Run Pyrogram bot
app.run()
