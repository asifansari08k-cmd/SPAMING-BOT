import asyncio

# --- ASYNCIO EVENT LOOP FIX FOR PYTHON 3.14+ ---
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# -----------------------------------------------

import random
import os
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode, UserStatus, ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait, PeerIdInvalid
from pyrogram.handlers import MessageHandler

# --- FLASK KEEP ALIVE SECTION ---
from flask import Flask
from threading import Thread

web_app = Flask('')

@web_app.route('/')
def home():
    return "Magma Manager Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
# --------------------------------------

# ==================== CONFIGURATION ====================
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
BOT_TOKEN = "8485202414:AAEEYv7_UjUR2DI4KN9l4bEKnsD9v0WGn7E"

OWNER_ID = 7727470646 # ✅ Aapki Owner ID

# Main Manager Bot
bot = Client("MagmaManager", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Storage for running clients
running_users = {} 

# ==================== GLOBAL STORAGE ====================
active_spams = {} 
auto_reply_users = {}
backup_profile = {} 
tagall_running = {}
active_bans = {} 
waiting_for_ad = {}
active_ads = {}
ad_content = {}

# --- START MESSAGE STORAGE (HARDCODED) ---
START_CHAT_ID = -1003804939396
START_MSG_ID = 3

# --- SHORT SPAM LIST ---
SPAM_MESSAGES = [
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗖𝗢𝗠𝗠𝗜𝗧 𝗞𝗥𝗨𝗚𝗔 𝗙𝗜𝗥 𝗧𝗘𝗥𝗜 𝗕𝗛𝗘𝗘𝗡 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗔𝗨𝗧𝗢𝗠𝗔𝗧𝗜𝗖𝗔𝗟𝗟𝗬 𝗨𝗣𝗗𝗔𝗧𝗘 𝗛𝗢𝗝𝗔𝗔𝗬𝗘𝗚𝗜 🤖🙏🤔",
    "{target} 𝗧𝗘𝗥𝗜 𝗠𝗨𝗠𝗠𝗬 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗞𝗢 𝗢𝗡𝗟𝗜𝗡𝗘 𝗢𝗟𝗫 𝗣𝗘 𝗕𝗘𝗖𝗛𝗨𝗡𝗚𝗔 𝗔𝗨𝗥 𝗣𝗔𝗜𝗦𝗘 𝗦𝗘 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗔 𝗞𝗢𝗧𝗛𝗔 𝗞𝗛𝗢𝗟 𝗗𝗨𝗡𝗚𝗔 😎🤩😝😍",
    "{target} 𝗧𝗘𝗥𝗜 𝗚𝗙 𝗛𝗘 𝗕𝗔𝗗𝗜 𝗦𝗘𝗫𝗬 𝗨𝗦𝗞𝗢 𝗣𝗜𝗟𝗔𝗞𝗘 𝗖𝗛𝗢𝗢𝗗𝗘𝗡𝗚𝗘 𝗣𝗘𝗣𝗦𝗜",
    "{target} 𝗚𝗔𝗟𝗜 𝗚𝗔𝗟𝗜 𝗠𝗘 𝗥𝗘𝗛𝗧𝗔 𝗛𝗘 𝗦𝗔𝗡𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔𝗞𝗢 𝗖𝗛𝗢𝗗 𝗗𝗔𝗟𝗔 𝗢𝗥 𝗕𝗔𝗡𝗔 𝗗𝗜𝗔 𝗥𝗔𝗡𝗗 🤤🤣"
]

# ==================== HELPER FUNCTIONS ====================

async def smart_edit(message, text, sleep_time=0.5):
    try:
        await message.edit(text, parse_mode=ParseMode.HTML)
        await asyncio.sleep(sleep_time)
    except FloodWait as e:
        if e.value < 6:
            await asyncio.sleep(e.value)
            try:
                await message.edit(text, parse_mode=ParseMode.HTML)
                await asyncio.sleep(sleep_time)
            except: pass
        else:
            pass 
    except: pass

async def draw_art(message, art_var, header="", footer="", chunk_size=4):
    lines = art_var.strip().split("\n")
    current_art = ""
    for i, line in enumerate(lines):
        current_art += line + "\n"
        if (i + 1) % chunk_size == 0 or i == len(lines) - 1:
            if header:
                display_text = f"<b>{header}</b>\n<code>{current_art}</code>"
            else:
                display_text = f"<code>{current_art}</code>"
            if i == len(lines) - 1 and footer:
                display_text += f"\n\n<b>{footer}</b>"
            await smart_edit(message, display_text, 0.5)

async def delete_res(message):
    await asyncio.sleep(5)
    try: await message.delete()
    except: pass

async def run_spam(client, chat_id, mention, count):
    global active_spams
    for i in range(count):
        if chat_id not in active_spams or not active_spams[chat_id]: break
        try:
            msg = random.choice(SPAM_MESSAGES).format(target=mention)
            await client.send_message(chat_id, msg, parse_mode=ParseMode.HTML)
            await asyncio.sleep(0.1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except: 
            continue
    active_spams[chat_id] = False

# ==================== ART ASSETS ====================
CAT_ANIMATION = ["🐈", "🐈\nWalking...", "🐈\nWalking...", "╱|、\n( .. )\n |、˜〵\nじしˍ,)ノ", "╱|、\n( > < )\n |、˜〵\nじしˍ,)ノ", "╱|、\n(˚ˎ 。7\n |、˜〵\nじしˍ,)ノ", "╱|、\n(˚ˎ 。7  < Meow! 🎵\n |、˜〵\nじしˍ,)ノ"]
FLOWER_BLOOM = ["🌱", "🌿\n🌿\n🌿", "🌷\n🌷\n🌷", "🌹\n🌹\n🌹"]
ROSE_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⢔⣒⠂⣀⣀⣤⣄⣀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣴⣿⠋⢠⣟⡼⣷⠼⣆⣼⢇⣿⣄⠱⣄
⠀⠀⠀⠀⠀⠀⠀⠹⣿⡀⣆⠙⠢⠐⠉⠉⣴⣾⣽⢟⡰⠃
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣦⠀⠤⢴⣿⠿⢋⣴⡏⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡙⠻⣿⣶⣦⣭⣉⠁⣿⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣷⠀⠈⠉⠉⠉⠉⠇⡟⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⣘⣦⣀⠀⠀⣀⡴⠊⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠛⢻⣿⣿⣿⣿⠻⣧⡀⠀⠀⠀
"""
HACKER_ART = r"""
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠁⠀⠀⠈⠉⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⢀⣠⣤⣤⣤⣤⣄⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⣤⣶⣤⣉⣿⣿⡯⣀⣴⣿⡗⠀⠀⠀⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡇⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⢸⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠉⢉⣽⣿⠿⣿⡿⢻⣯⡍⢁⠄⠀⠀⠀⣸⣿⣿⣿⣿
"""
ERROR_ART = r"""
▒▒▒▒▒▒▒▒▄▄▄▄▄▄▄▄▒▒▒▒▒▒
▒▒█▒▒▒▄██████████▄▒▒▒▒
▒█▐▒▒▒████████████▒▒▒▒
▒▌▐▒▒██▄▀██████▀▄██▒▒▒
▐┼▐▒▒██▄▄▄▄██▄▄▄▄██▒▒▒
▐┼▐▒▒██████████████▒▒▒
▐▄▐████─▀▐▐▀█─█─▌▐██▄▒
"""
FUCK_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⢀⡤⠤⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣾⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⡏⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⡾⠋⠻⡇⠀⠀⢸⣧⣀⡀⠀⠀⠀⠀
⠀⠀⢀⣾⠁⠀⠀⡇⠀⠀⢸⠁⠀⢹⣀⠀⠀⠀
⢀⡴⠋⡟⠀⠀⢠⡇⠀⠀⢸⠀⠀⠀⡇⠉⢆⠀
⡎⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠀⠈⣆
"""
BUTTERFLY_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢔⣶⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⠀⠀⡼⠗⡿⣾⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢄⣀⠀⠀⠀⡇⢀⡼⠓⡞⢩⣯⡀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⠀⠀⠀⠀⠉⠳⢜⠰⡹⠁⢰⠃⣩⣿⡇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⣿⠿⣉⣩⠛⠲⢶⡠⢄⢙⣣⠃⣰⠗⠋⢀⣯⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣯⣠⠬⠦⢤⣀⠈⠓⢽⣿⢔⣡⡴⠞⠻⠙⢳⡄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣵⣳⠖⠉⠉⢉⣩⣵⣿⣿⣒⢤⣴⠤⠽⣬⡇
"""
YOURMOM_ART = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣾⣶⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠐⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⡿⠟⣡⣴⣦⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⡀⠀⠀⠀⠀⠀⠀
"""
MYSON_ART = r"""
  ⠀     (\__/)
      (•ㅅ•)      Don’t talk to
   ＿ノヽ ノ＼＿      me or my son
/　/ ⌒Ｙ⌒ Ｙ  ヽ     ever again.
( 　(三ヽ人　 /　  |
|　ﾉ⌒＼ ￣￣ヽ   ノ
ヽ＿＿＿＞､＿_／
      ｜( 王 ﾉ〈  (\__/)
      /ﾐ`ー―彡\  (•ㅅ•)
     / ╰    ╯ \ /    \>
"""

# ==================== USERBOT HANDLERS ====================

async def help_handler(client, message):
    text = """
🔥 **GOURISEN OSINT USERBOT COMMANDS** 🔥

🐱 `.cat` - Cute Cat Animation
🌹 `.rose` - Rose Animation
💻 `.hacker` - Hacking Animation
⚠️ `.error` - System Crash Animation
🖕 `.fuck` - Middle Finger Animation
🦋 `.butterfly` - Draw Butterfly
🤱 `.yourmom` - Mom Roast Animation
🐰 `.myson` - Me & My Son
❤️ `.love` - Magic Heart Animation
ℹ️ `.info <reply>` - Get User Info
🚀 `.spam <msg> <count>` - Custom Spam
🚀 `.gourisenosint <username/id> <count>` - Abuse Spam
🎯 `.agourisenosint` - Global Auto-Reply
👥 `.clone` - Copy ID
🔄 `.back` - Restore ID
📍 `.tagall <msg>` - Tag Everyone
🔨 `.allban <id>` - Ban members (0.5s delay)
⚡ `.fastallban <id>` - Fast ban (0.2s - 0.3s delay)
☠️ `.end <id>` - Nuke GC (Extreme Speed)
📢 `.ad` - Setup Auto Group Ad (5 min)
🛑 `.stopad` - Stop Auto Ad
🛑 `.stop` - Stop All Tasks
"""
    try: await message.edit(text)
    except:
        try: await client.send_message(message.chat.id, text)
        except: pass

async def cat_handler(client, message):
    for frame in CAT_ANIMATION: await smart_edit(message, f"<code>{frame}</code>")

async def rose_handler(client, message):
    for frame in FLOWER_BLOOM: await smart_edit(message, f"<code>{frame}</code>", 0.6)
    await draw_art(message, ROSE_ART, footer="🌹 **FOR YOU!**")

async def hacker_handler(client, message):
    await smart_edit(message, "💻 **Hacking System...**")
    await draw_art(message, HACKER_ART, footer="💻 **SYSTEM HACKED!**")

async def error_handler(client, message):
    await smart_edit(message, "⚠️ **SYSTEM CRASHING...**")
    await draw_art(message, ERROR_ART, footer="⚠️ **FATAL ERROR DETECTED!**")

async def fuck_handler(client, message):
    await smart_edit(message, "🖕 **Loading...**")
    await draw_art(message, FUCK_ART, footer="🖕 **FUCK YOU!**")

async def butterfly_handler(client, message):
    await smart_edit(message, "🦋 **Drawing...**")
    await draw_art(message, BUTTERFLY_ART, footer="🦋 **Fly High!**")

async def love_handler(client, message):
    frames = [
        "❤️🧡💛💚💙💜🖤🤍🤎\n❤️🧡💛💚💙💜🖤🤍🤎\n❤️🧡💛💚💙💜🖤🤍🤎",
        "🧡💛💚💙💜🖤🤍🤎❤️\n🧡💛💚💙💜🖤🤍🤎❤️\n🧡💛💚💙💜🖤🤍🤎❤️",
        "💛💚💙💜🖤🤍🤎❤️🧡\n💛💚💙💜🖤🤍🤎❤️🧡\n💛💚💙💜🖤🤍🤎❤️🧡",
        "💚💙💜🖤🤍🤎❤️🧡💛\n💚💙💜🖤🤍🤎❤️🧡💛\n💚💙💜🖤🤍🤎❤️🧡💛",
        "💙💜🖤🤍🤎❤️🧡💛💚\n💙💜🖤🤍🤎❤️🧡💛💚\n💙💜🖤🤍🤎❤️🧡💛💚",
        "💜🖤🤍🤎❤️🧡💛💚💙\n💜🖤🤍🤎❤️🧡💛💚💙\n💜🖤🤍🤎❤️🧡💛💚💙",
        "🖤🤍🤎❤️🧡💛💚💙💜\n🖤🤍🤎❤️🧡💛💚💙💜\n🖤🤍🤎❤️🧡💛💚💙💜",
        "🤍🤎❤️🧡💛💚💙💜🖤\n🤍🤎❤️🧡💛💚💙💜🖤\n🤍🤎❤️🧡💛💚💙💜🖤",
        "🤎❤️🧡💛💚💙💜🖤🤍\n🤎❤️🧡💛💚💙💜🖤🤍\n🤎❤️🧡💛💚💙💜🖤🤍",
        "❤️❤️❤️❤️❤️❤️❤️❤️❤️\n❤️❤️❤️❤️❤️❤️❤️❤️❤️\n❤️❤️❤️❤️❤️❤️❤️❤️❤️",
        "<b>I LOVE YOU ❤️</b>"
    ]
    for frame in frames: await smart_edit(message, frame, 0.6)

async def yourmom_handler(client, message):
    await smart_edit(message, "🤱 **Searching for Mom...**")
    await smart_edit(message, "🫦 **Target Locked!**")
    await draw_art(message, YOURMOM_ART, header="🤱 Gourisen OSINT USER'S VS YOUR MOM 💋", footer="TERI MAA MERI LUND PE 🥵💋")

async def myson_handler(client, message):
    await smart_edit(message, "🐰 **Summoning Son...**")
    await draw_art(message, MYSON_ART)

async def info_cmd(client, message):
    target_id = message.command[1] if len(message.command) > 1 else (message.reply_to_message.from_user.id if message.reply_to_message else "me")
    status_msg = await message.edit("Processing . . .")
    try:
        user = await client.get_users(target_id)
        chat = await client.get_chat(target_id)
        try: common = len(await client.get_common_chats(user.id))
        except: common = 0
        status_map = {UserStatus.ONLINE:"Online 🟢", UserStatus.OFFLINE:"Offline ⚫", UserStatus.RECENTLY:"Recently 🟡"}
        status = status_map.get(user.status, "Unknown")
        link = f"<a href='tg://user?id={user.id}'>ㅤ❛ .𝁘ໍ⸼ ‌‌ 𝐌 𝐀 𝐆 𝐌 𝐀 𐏓𝟑 🪙</a>" if user.id == 8081343902 else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

        caption = f"""USER INFORMATION:
🆔 User ID: <code>{user.id}</code>
👤 First Name: {user.first_name}
🗣️ Last Name: {user.last_name or "-"}
🌐 Username: @{user.username or "-"}
🏛️ DC ID: {user.dc_id or "-"}
🤖 Is Bot: {user.is_bot}
🚷 Is Scam: {user.is_scam}
🚫 Restricted: {user.is_restricted}
✅ Verified: {user.is_verified}
⭐ Premium: {user.is_premium or False}
📝 User Bio: {chat.bio or "-"}
👀 Same groups seen: {common}
👁️ Last Seen: {status}
🔗 User permanent link: {link}"""
        photos = [p async for p in client.get_chat_photos(user.id, limit=1)]
        if photos:
            await status_msg.delete()
            await client.send_photo(message.chat.id, photo=photos[0].file_id, caption=caption, parse_mode=ParseMode.HTML)
        else: await status_msg.edit(caption, parse_mode=ParseMode.HTML)
    except Exception as e: 
        await status_msg.edit(f"❌ Error: {e}")
        asyncio.create_task(delete_res(status_msg))

async def clone_cmd(client, message):
    global backup_profile
    if not message.reply_to_message:
        res = await message.edit("❌ Reply to clone!")
        return asyncio.create_task(delete_res(res))
    target = message.reply_to_message.from_user
    await message.edit(f"👤 Cloning {target.first_name}...")
    try:
        me = await client.get_me()
        backup_profile[me.id] = {"fn": me.first_name, "ln": me.last_name or "", "bio": (await client.get_chat("me")).bio or ""}
        async for p in client.get_chat_photos("me", limit=1): backup_profile[me.id]["photo"] = await client.download_media(p.file_id)

        full_t = await client.get_chat(target.id)
        await client.update_profile(first_name=target.first_name or "", last_name=target.last_name or "", bio=full_t.bio or "")
        async for p in client.get_chat_photos(target.id, limit=1):
            path = await client.download_media(p.file_id)
            await client.set_profile_photo(photo=path)
            if os.path.exists(path): os.remove(path)
        res = await message.edit(f"✅ Cloned: {target.first_name}")
    except Exception as e: res = await message.edit(f"❌ Error: {e}")
    asyncio.create_task(delete_res(res))

async def back_cmd(client, message):
    global backup_profile
    me_id = client.me.id
    if me_id not in backup_profile:
        res = await message.edit("❌ No backup found!")
        return asyncio.create_task(delete_res(res))
    await message.edit("🔄 Restoring...")
    try:
        data = backup_profile[me_id]
        await client.update_profile(first_name=data["fn"], last_name=data["ln"], bio=data["bio"])
        if "photo" in data: await client.set_profile_photo(photo=data["photo"])
        res = await message.edit("✅ Profile Restored!")
    except Exception as e: res = await message.edit(f"❌ Error: {e}")
    asyncio.create_task(delete_res(res))

async def spam_cmd(client, message):
    global active_spams
    args = message.command
    if len(args) < 3:
        res = await message.edit("❌ **Usage:** `.spam <message> <count>`")
        return asyncio.create_task(delete_res(res))
    try:
        try:
            count, spam_text = int(args[-1]), " ".join(args[1:-1])
        except ValueError:
            count, spam_text = int(args[1]), " ".join(args[2:])
        if not spam_text:
            res = await message.edit("❌ Spam message daalna bhool gaye!")
            return asyncio.create_task(delete_res(res))
        chat_id = message.chat.id
        active_spams[chat_id] = True
        await message.delete()
        for _ in range(count):
            if not active_spams.get(chat_id, True): break
            try:
                await client.send_message(chat_id, spam_text)
                await asyncio.sleep(0.1) 
            except FloodWait as e: await asyncio.sleep(e.value)
            except: continue
    except Exception as e:
        res = await message.edit(f"❌ Error: {e}")
        asyncio.create_task(delete_res(res))

async def gourisenosint_cmd(client, message):
    global active_spams
    args = message.command
    if len(args) < 2:
        res = await message.edit("❌ Usage:\n`.gourisenosint <count>` (Reply)\n`.gourisenosint <username/id> <count>`")
        return asyncio.create_task(delete_res(res))
    try:
        if message.reply_to_message:
            count, target = int(args[1]), message.reply_to_message.from_user
        else:
            if len(args) < 3:
                res = await message.edit("❌ Usage: `.gourisenosint <username/id> <count>`")
                return asyncio.create_task(delete_res(res))
            target_input, count = args[1], int(args[2])
            try: target = await client.get_users(int(target_input) if target_input.lstrip('-').isdigit() else target_input)
            except:
                res = await message.edit(f"❌ User not found.")
                return asyncio.create_task(delete_res(res))
        mention = f"<a href='tg://user?id={target.id}'>{target.first_name}</a>"
        active_spams[message.chat.id] = True
        res = await message.edit(f"🚀 **Fast Spamming {count} on {mention}...**")
        asyncio.create_task(run_spam(client, message.chat.id, mention, count))
        asyncio.create_task(delete_res(res))
    except ValueError:
        res = await message.edit("❌ Count must be a number!")
        asyncio.create_task(delete_res(res))
    except Exception as e:
        res = await message.edit(f"❌ Error: {e}")
        asyncio.create_task(delete_res(res))

async def agourisenosint_cmd(client, message):
    global auto_reply_users
    if not message.reply_to_message:
        res = await message.edit("❌ Reply to target!")
        return asyncio.create_task(delete_res(res))
    target = message.reply_to_message.from_user
    mention = f"<a href='tg://user?id={target.id}'>{target.first_name}</a>"
    auto_reply_users[target.id] = mention
    res = await message.edit(f"🎯 Global Auto-Reply: {mention}")
    asyncio.create_task(delete_res(res))

async def tagall_cmd(client, message):
    global tagall_running
    chat_id = message.chat.id
    tagall_running[chat_id] = True
    msg = " ".join(message.command[1:]) if len(message.command) > 1 else ""
    await message.delete()
    async for m in client.get_chat_members(chat_id):
        if not tagall_running.get(chat_id): break
        if m.user.is_bot: continue
        try:
            await client.send_message(chat_id, f"<a href='tg://user?id={m.user.id}'>{m.user.first_name}</a>\n{msg}", parse_mode=ParseMode.HTML)
            await asyncio.sleep(1.5)
        except: continue
    tagall_running[chat_id] = False

async def allban_cmd(client, message):
    global active_bans
    if len(message.command) < 2:
        res = await message.edit("❌ Usage: `.allban <chat_id or username>`")
        return asyncio.create_task(delete_res(res))
    chat_id = message.command[1]
    try: chat_id = int(chat_id) if chat_id.lstrip('-').isdigit() else chat_id
    except: pass
    active_bans[message.chat.id] = True
    status_msg = await message.edit(f"🔨 **Mass ban started...**\n(0.5s delay)")
    me = await client.get_me()
    banned_count = 0
    try:
        async for member in client.get_chat_members(chat_id):
            if not active_bans.get(message.chat.id, True):
                await status_msg.edit(f"🛑 **Mass ban stopped!** Banned {banned_count}.")
                return
            if member.user.id == me.id: continue
            try:
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
            except: continue
        if active_bans.get(message.chat.id, True): await status_msg.edit(f"✅ **Mass ban complete!** Banned {banned_count}.")
    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {e}")
        asyncio.create_task(delete_res(status_msg))

async def fastallban_cmd(client, message):
    global active_bans
    if len(message.command) < 2:
        res = await message.edit("❌ Usage: `.fastallban <chat_id or username>`")
        return asyncio.create_task(delete_res(res))
    chat_id = message.command[1]
    try: chat_id = int(chat_id) if chat_id.lstrip('-').isdigit() else chat_id
    except: pass
    active_bans[message.chat.id] = True
    status_msg = await message.edit(f"⚡ **FAST Mass ban started...**")
    me = await client.get_me()
    banned_count = 0
    try:
        async for member in client.get_chat_members(chat_id):
            if not active_bans.get(message.chat.id, True): return
            if member.user.id == me.id: continue
            try:
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
                await asyncio.sleep(random.uniform(0.2, 0.3)) 
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
            except: continue
        if active_bans.get(message.chat.id, True): await status_msg.edit(f"✅ **Fast Mass ban complete!** Banned {banned_count}.")
    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {e}")
        asyncio.create_task(delete_res(status_msg))

async def end_cmd(client, message):
    global active_bans
    if len(message.command) < 2:
        res = await message.edit("❌ Usage: `.end <chat_id>`")
        return asyncio.create_task(delete_res(res))
    chat_id = message.command[1]
    try: chat_id = int(chat_id) if chat_id.lstrip('-').isdigit() else chat_id
    except: pass
    active_bans[message.chat.id] = True
    status_msg = await message.edit(f"☠️ **NUKE GC started...**")
    me = await client.get_me()
    banned_count = 0
    try:
        async for member in client.get_chat_members(chat_id):
            if not active_bans.get(message.chat.id, True): return
            if member.user.id == me.id: continue
            try:
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
                await asyncio.sleep(0.05) 
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.ban_chat_member(chat_id, member.user.id)
                banned_count += 1
            except: continue
    except: pass 
    if not active_bans.get(message.chat.id, True): return
    try: await client.set_chat_title(chat_id, "FUCK BY Gourisen OSINT USER")
    except: pass
    owner_mention = "Owner"
    try:
        async for admin in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if admin.status == ChatMemberStatus.OWNER:
                owner_mention = f"<a href='tg://user?id={admin.user.id}'>{admin.user.first_name}</a>"
                break
    except: pass
    try:
        sent_msg = await client.send_message(chat_id, f"{owner_mention}\nME KYA LADLE MEAOOOUUUUUU\nGOP GOP GOP GOP GOP 🥳", parse_mode=ParseMode.HTML)
        try: await sent_msg.pin(both_sides=True)
        except: await sent_msg.pin()
    except: pass
    await status_msg.edit(f"✅ **Nuke complete!** Banned {banned_count} members.")

async def run_ad_loop(client, user_id):
    global active_ads, ad_content
    while active_ads.get(user_id, False):
        try:
            async for dialog in client.get_dialogs():
                if not active_ads.get(user_id, False): break
                chat = dialog.chat
                if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                    try:
                        await client.send_message(chat.id, ad_content[user_id], parse_mode=ParseMode.HTML)
                        await asyncio.sleep(1.5) 
                    except FloodWait as e: await asyncio.sleep(e.value)
                    except: continue
            if active_ads.get(user_id, False): await asyncio.sleep(300) 
        except: break

async def ad_setup_cmd(client, message):
    global waiting_for_ad
    user_id = message.from_user.id
    waiting_for_ad[user_id] = True
    await message.edit("📢 **AD SETUP**\n\nAb niche ek naya message bhejo jo aapko sabhi groups me automatically bhejna hai:")

async def ad_listener(client, message):
    global waiting_for_ad, active_ads, ad_content
    user_id = message.from_user.id
    if waiting_for_ad.get(user_id):
        waiting_for_ad[user_id] = False
        ad_content[user_id] = message.text.html if message.text else "Ad Message"
        active_ads[user_id] = True
        await message.reply(f"✅ **Ad Successfully Set!**")
        asyncio.create_task(run_ad_loop(client, user_id))

async def stopad_cmd(client, message):
    global active_ads
    user_id = message.from_user.id
    if user_id in active_ads: active_ads[user_id] = False
    res = await message.edit("🛑 **Ad Broadcast Stopped!**")
    asyncio.create_task(delete_res(res))

async def stop_cmd(client, message):
    global active_spams, tagall_running, auto_reply_users, active_bans, active_ads
    user_id = message.from_user.id
    active_spams[message.chat.id] = False
    tagall_running[message.chat.id] = False
    active_bans[message.chat.id] = False 
    auto_reply_users.clear()
    if user_id in active_ads: active_ads[user_id] = False 
    res = await message.edit("🛑 **All Tasks Stopped!**")
    asyncio.create_task(delete_res(res))

async def auto_reply_listener(client, message):
    global auto_reply_users
    if not message.from_user: return
    if message.from_user.id in auto_reply_users:
        mention = auto_reply_users[message.from_user.id]
        msg = random.choice(SPAM_MESSAGES).format(target=mention)
        try: await message.reply(msg, parse_mode=ParseMode.HTML)
        except: pass

async def ad_filter_func(_, __, message):
    if not message.from_user: return False
    return bool(waiting_for_ad.get(message.from_user.id, False))
ad_filter = filters.create(ad_filter_func)


# ==================== MAIN BOT START HANDLER ====================
# YAHAN PE EXACT QUOTE (REPLY) KAREGA JAISE PURANA KARTA THA

@bot.on_message(filters.command("setstart") & filters.user(OWNER_ID))
async def set_start_cmd(client, message):
    global START_CHAT_ID, START_MSG_ID
    if len(message.command) < 2:
        await message.reply("❌ Usage: `/setstart <link>`")
        return
    link = message.command[1]
    try:
        parts = link.rstrip("/").split("/")
        START_MSG_ID = int(parts[-1])
        chat_part = parts[-2]
        START_CHAT_ID = int(f"-100{chat_part}") if chat_part.isdigit() else chat_part
        await message.reply(f"✅ **Start message updated!**")
    except Exception as e:
        await message.reply(f"❌ **Invalid link:** `{e}`")

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if not START_CHAT_ID or not START_MSG_ID:
        await message.reply("Hᴇʏ! Start message abhi set nahi hai.\nOwner ko bolo `/setstart <link>` use karke pehle message set kare ✨", quote=True)
        return
    
    try:
        # Channel se message get karna 
        m = await client.get_messages(START_CHAT_ID, START_MSG_ID)
        
        if not m:
            return await message.reply("❌ Message nahi mila channel me.", quote=True)
            
        # Exact quote karke user ko send karna (Photo/Video/Text)
        if m.photo:
            await message.reply_photo(photo=m.photo.file_id, caption=m.caption or "", caption_entities=m.caption_entities, quote=True)
        elif m.video:
            await message.reply_video(video=m.video.file_id, caption=m.caption or "", caption_entities=m.caption_entities, quote=True)
        elif m.text:
            await message.reply_text(text=m.text, entities=m.entities, quote=True)
        else:
            await client.copy_message(chat_id=message.chat.id, from_chat_id=START_CHAT_ID, message_id=START_MSG_ID, reply_to_message_id=message.id)
            
    except PeerIdInvalid:
        await message.reply("⚠️ **Pyrogram ko channel ka rasta nahi mil raha.**\n\n🛠 **Solve kaise karein:**\nBot ko channel me admin bana rakha hai toh, apne channel me jao aur bas `Hi` likh kar bhej do bot ko. Bot update pakad lega aur error hat jayega!", quote=True)
    except Exception as e:
        await message.reply(f"❌ **Error:** `{e}`", quote=True)


# ==================== SESSION ADDER ====================

@bot.on_message(filters.command("add") & filters.private)
async def add_session_handler(client, message):
    if len(message.command) < 2:
        await message.reply("❌ Usage: `/add <StringSession>`")
        return

    session_string = message.text.split(None, 1)[1]
    msg = await message.reply("🔄 Connecting...")

    try:
        new_user = Client(
            name=f"user_{random.randint(1000, 9999)}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string,
            in_memory=True
        )

        await new_user.start()
        me = await new_user.get_me()

        new_user.add_handler(MessageHandler(help_handler, filters.command("help", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(cat_handler, filters.command("cat", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(rose_handler, filters.command("rose", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(hacker_handler, filters.command("hacker", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(error_handler, filters.command("error", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(fuck_handler, filters.command("fuck", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(butterfly_handler, filters.command("butterfly", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(love_handler, filters.command("love", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(yourmom_handler, filters.command("yourmom", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(myson_handler, filters.command("myson", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(info_cmd, filters.command("info", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(clone_cmd, filters.command("clone", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(back_cmd, filters.command("back", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(spam_cmd, filters.command("spam", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(gourisenosint_cmd, filters.command("gourisenosint", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(agourisenosint_cmd, filters.command("agourisenosint", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(tagall_cmd, filters.command("tagall", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(allban_cmd, filters.command("allban", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(fastallban_cmd, filters.command("fastallban", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(end_cmd, filters.command("end", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(ad_setup_cmd, filters.command("ad", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(stopad_cmd, filters.command("stopad", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(stop_cmd, filters.command("stop", prefixes=".") & filters.me))

        new_user.add_handler(MessageHandler(ad_listener, ad_filter & filters.me))
        new_user.add_handler(MessageHandler(auto_reply_listener, filters.incoming & ~filters.me))

        running_users[me.id] = new_user

        await msg.edit(f"✅ **Connected Successfully!**\nUser: {me.first_name}\nID: `{me.id}`\n\nMagma Bot is now active on your account.")
        print(f"User {me.first_name} started.")

    except Exception as e:
        await msg.edit(f"❌ **Connection Failed!**\nError: {e}")

print("✅ Magma Manager Bot Online!")

keep_alive()
bot.run()