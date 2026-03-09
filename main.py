# ==================== MAIN BOT LOGIC ====================

# -- ASYNCIO EVENT LOOP FIX (Wahi purana) --
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# -----------------------------------------------

# Configuration (Wahi purana)
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
BOT_TOKEN = "8485202414:AAEEYv7_UjUR2DI4KN9l4bEKnsD9v0WGn7E"
OWNER_ID = 7727470646 
FORCE_CHANNEL_ID = -1003892920891  
FORCE_CHANNEL_LINK = "https://t.me/+Om1HMs2QTHk1N2Zh" 
FORCE_GROUP = "Anysnapsupport"

# Start and Addstart Logic (Updated with exact media bot logic, formating preserved, no buttons)
START_DATA = {
    "type": "text",      # Photo, video, text
    "file_id": None,     # Media unique code
    "text": None,        # Message or caption
    "entities": None     # Premium Emojis, bold, italic formating
}

# Force subscribe logic (Preserved)
async def check_force_subscribe(client, message):
    user_id = message.from_user.id
    try:
        await client.get_chat_member(FORCE_CHANNEL_ID, user_id)
        # Assuming FORCE_GROUP check isn't strictly necessary or is covered,
        # but maintaining original provided code as much as possible, 
        # as user didn't request change here.
        # await client.get_chat_member(FORCE_GROUP, user_id) 
        return True
    except UserNotParticipant:
        await message.reply(
            "**⛔ ACCESS DENIED!**\n\n"
            "You must join our Channel to use this bot.\n"
            "Join then try again!",
            parse_mode=ParseMode.HTML # Force subscribe message formatting
        )
        return False
    except Exception as e:
        print(f"FS Error: {e}")
        return True 

bot = Client("MagmaManager", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def ad_filter_func(_, __, message):
    if not message.from_user:
        return False
    return bool(waiting_for_ad.get(message.from_user.id, False))
ad_filter = filters.create(ad_filter_func)


# --- UPDATED START AND ADDSTART LOGIC ---

@bot.on_message(filters.command("addstart") & filters.user(OWNER_ID) & filters.private)
async def save_start_with_media(client, message):
    global START_DATA
    
    if not message.reply_to_message:
        await message.reply_text("⚠️ Bhai, pehle message (photo/video/text) bhejo, fir us par reply karke `/addstart` likho!")
        return
    
    reply = message.reply_to_message
    
    # Save photo with caption formatting
    if reply.photo:
        START_DATA["type"] = "photo"
        START_DATA["file_id"] = reply.photo.file_id
        START_DATA["text"] = reply.caption
        START_DATA["entities"] = reply.caption_entities
        await message.reply_text("🖼️ **Photo aur Premium Emojis dono save ho gaye!**")

    # Save video with caption formatting
    elif reply.video:
        START_DATA["type"] = "video"
        START_DATA["file_id"] = reply.video.file_id
        START_DATA["text"] = reply.caption
        START_DATA["entities"] = reply.caption_entities
        await message.reply_text("🎥 **Video aur Premium Emojis dono save ho gaye!**")

    # Save text with all its formatting
    elif reply.text:
        START_DATA["type"] = "text"
        START_DATA["file_id"] = None
        START_DATA["text"] = reply.text
        START_DATA["entities"] = reply.entities
        await message.reply_text("📝 **Text aur Premium Emojis save ho gaye!**")
        
    else:
        await message.reply_text("⚠️ **Ye format support nahi kar raha, bhai. Photo, Video ya Text bhejo.**")


@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if not await check_force_subscribe(client, message):
        return

    global START_DATA
    # Buttons setup removed as requested.

    try:
        if START_DATA["type"] == "photo" and START_DATA["file_id"]:
            await message.reply_photo(
                photo=START_DATA["file_id"], 
                caption=START_DATA["text"], 
                caption_entities=START_DATA["entities"] 
                # reply_markup removed
            )
            
        elif START_DATA["type"] == "video" and START_DATA["file_id"]:
            await message.reply_video(
                video=START_DATA["file_id"], 
                caption=START_DATA["text"], 
                caption_entities=START_DATA["entities"] 
                # reply_markup removed
            )
            
        elif START_DATA["type"] == "text" and START_DATA["text"]:
            await message.reply_text(
                text=START_DATA["text"], 
                entities=START_DATA["entities"] 
                # reply_markup removed
            )
            
        else:
            # New, clean text default start message without buttons.
            # Updated to match the content of the user's provided bot text.
            text = """
<b>m🅰️gm🅰️</b>

📣 <b>Magma Bot WELCOME TO MAGMA USERBOT MANAGER</b>

💬 I can help you run the powerful Magma Userbot on your Telegram account

1️⃣ <b>HOW TO START</b>
💬 Get Session
⚙️ Go to: @Stingxsessionbot
Generate a Pyrogram String Session.

2️⃣ <b>Connect</b>
🔥 Send the session here using command:/add string session

3️⃣ <b>Enjoy</b>
⚡ After connecting, go to Saved Messages.
Type: .help to see all commands

⚠️ <b>NOTE</b>
🛡️ Keep your String Session safe
👤 Never share it with anyone
"""
            await message.reply_text(text, parse_mode=ParseMode.HTML) # No buttons.
            
    except Exception as e:
        await message.reply_text(f"**Error aagaya bhai:** {e}")


@bot.on_message(filters.command("add") & filters.private)
async def add_session_handler(client, message):
    if not await check_force_subscribe(client, message):
        return

    if len(message.command) < 2:
        await message.reply("❌ **Usage:** `/add <StringSession>`")
        return

    session_string = message.text.split(None, 1)[1]
    msg = await message.reply("🔄 **Connecting...**")

    # The rest of the userbot client setup remains the same.
    # No changes were requested for this part.
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

        # Added handlers (same same)
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
        new_user.add_handler(MessageHandler(anysnap_cmd, filters.command("anysnap", prefixes=".") & filters.me))
        new_user.add_handler(MessageHandler(aanysnap_cmd, filters.command("aanysnap", prefixes=".") & filters.me))
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

        await msg.edit(f"✅ **Connected Successfully!**\n**User:** {me.first_name}\n**ID:** `{me.id}`\n\n**Magma Bot is now active on your account.**")
        print(f"User {me.first_name} started.")

    except Exception as e:
        await msg.edit(f"❌ **Connection Failed!**\n**Error:** {e}")

# (Wahi purana end of MAIN BOT LOGIC)
print("✅ Magma Manager Bot Online!")
keep_alive()
bot.run()