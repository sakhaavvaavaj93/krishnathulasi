
import asyncio
from config import Config
from utils import USERNAME, mp
from pyrogram import Client, filters, emoji
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

msg=Config.msg
ADMINS=Config.ADMINS
playlist=Config.playlist


HOME_TEXT = "👋🏻 **Hi [{}](tg://user?id={})**,\n\nI'm **𝐃𝐂 𝙿𝙻𝙰𝚈𝙴𝚁** \nI Can Play Radio / Music / YouTube Live In Channel & Group 24x7 Nonstop. Made with ❤️ By @KRISHNA_THULSI😉!"
HELP_TEXT = """
💡 --**Setting Up**--:

\u2022 Add the bot and user account in your group with admin rights.
\u2022 Start a voice chat in your group & restart the bot if not joined to vc.
\u2022 Use /play [song name] or use /play as a reply to an audio file or youtube link.

💡 --**Common Commands**--:

\u2022 `/help` - shows help for all commands
\u2022 `/song` [song name] - download the song as audio


💡 --**Admins Commands**--:

\u2022 `/radio` - start radio stream
\u2022 `/stopradio` - stop radio stream
\u2022 `/skip` - skip current music
\u2022 `/stop` - stop playing music
\u2022 `/volume` - change volume (0-200)
\u2022 `/replay` - play from the beginning
\u2022 `/clean` - remove unused raw files
\u2022 `/pause` - pause playing music
\u2022 `/resume` - resume playing music
\u2022 `/mute` - mute the vc userbot
\u2022 `/unmute` - unmute the vc userbot
\u2022 `/restart` - update & restart the bot
\u2022 `/setvar` - set/change heroku configs

© **Powered By** : 
**@DC_LOGS | @KRISHNA_THULSI** 👑
"""


@Client.on_message(filters.command(["start", f"start@{USERNAME}"]))
async def start(client, message):
    buttons = [
            [
                InlineKeyboardButton("SEARCH SONGS INLINE", switch_inline_query_current_chat=""),
            ],
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/AsmSafone"),
                InlineKeyboardButton("SUPPORT", url="https://t.me/AsmSupport"),
            ],
            [
                InlineKeyboardButton("MORE BOTS", url="https://t.me/AsmSafone/173"),
                InlineKeyboardButton("SOURCE CODE", url="https://github.com/AsmSafone/RadioPlayerV3"),
            ],
            [
                InlineKeyboardButton("❔ HOW TO USE ❔", callback_data="help"),
            ]
            ]
    reply_markup = InlineKeyboardMarkup(buttons)
    m=await message.reply_photo(photo="http://telegra.ph/file/5935c9e008a2675c100f3.jpg", caption=HOME_TEXT.format(message.from_user.first_name, message.from_user.id), reply_markup=reply_markup)
    await mp.delete(m)
    await mp.delete(message)


@Client.on_message(filters.command(["help", f"help@{USERNAME}"]))
async def help(client, message):
    buttons = [
            [
                InlineKeyboardButton("SEARCH SONGS INLINE", switch_inline_query_current_chat=""),
            ],
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/AsmSafone"),
                InlineKeyboardButton("SUPPORT", url="https://t.me/AsmSupport"),
            ],
            [
                InlineKeyboardButton("MORE BOTS", url="https://t.me/AsmSafone/173"),
                InlineKeyboardButton("SOURCE CODE", url="https://github.com/AsmSafone/RadioPlayerV3"),
            ],
            [
                InlineKeyboardButton("BACK HOME", callback_data="home"),
                InlineKeyboardButton("CLOSE MENU", callback_data="close"),
            ]
            ]
    reply_markup = InlineKeyboardMarkup(buttons)
    if msg.get('help') is not None:
        await msg['help'].delete()
    msg['help'] = await message.reply_photo(photo="http://telegra.ph/file/5935c9e008a2675c100f3.jpg", caption=HELP_TEXT, reply_markup=reply_markup)
    await mp.delete(message)



