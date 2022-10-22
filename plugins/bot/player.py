
import os
import re
import ffmpeg
import asyncio
import subprocess
from config import Config
from signal import SIGINT
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
from pyrogram import Client, filters, emoji
from utils import mp, RADIO, USERNAME, FFMPEG_PROCESSES
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


msg=Config.msg
playlist=Config.playlist
ADMINS=Config.ADMINS
RADIO_TITLE=Config.RADIO_TITLE
EDIT_TITLE=Config.EDIT_TITLE
ADMIN_ONLY=Config.ADMIN_ONLY
DURATION_LIMIT=Config.DURATION_LIMIT

async def is_admin(_, client, message: Message):
    admins = await mp.get_admins
    if message.from_user is None and message.sender_chat:
        return True
    if message.from_user.id in admins:
        return True
    else:
        return False

ADMINS_FILTER = filters.create(is_admin)


@Client.on_message(filters.command(["play", f"play@{USERNAME}"]) & filters.audio & filters.private)
async def yplay(_, message: Message):
    if ADMIN_ONLY == "True":
        admins = await mp.get_admins
        if message.from_user.id not in admins:
            m=await message.reply_sticker("CAACAgIAAx0Cb2zEwgADJ2NTyZ8qXw08hqL5Zgihy414-Uu-AAItAQACMNSdERCGBLkvnsTRKgQ")
            await mp.delete(m)
            await mp.delete(message)
            return
    type=""
    yturl=""
    ysearch=""
    if message.audio:
        type="audio"
        m_audio = message
    elif message.reply_to_message and message.reply_to_message.audio:
        type="audio"
        m_audio = message.reply_to_message
    else:
        if message.reply_to_message:
            link=message.reply_to_message.text
            regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
            match = re.match(regex,link)
            if match:
                type="youtube"
                yturl=link
        elif " " in message.text:
            text = message.text.split(" ", 1)
            query = text[1]
            regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
            match = re.match(regex,query)
            if match:
                type="youtube"
                yturl=query
            else:
                type="query"
                ysearch=query
        else:
            d=await message.reply_text("❗️ __You Didn't Give Me Anything To Play, Send Me An Audio File or Reply /play To An Audio File!__")
            await mp.delete(d)
            await mp.delete(message)
            return
    user=f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    group_call = mp.group_call
    if type=="audio":
        if round(m_audio.audio.duration / 60) > DURATION_LIMIT:
            d=await message.reply_text(f"❌ __Audios Longer Than {DURATION_LIMIT} Minute(s) Aren't Allowed, The Provided Audio Is {round(m_audio.audio.duration/60)} Minute(s)!__")
            await mp.delete(d)
            await mp.delete(message)
            return
        if playlist and playlist[-1][2] == m_audio.audio.file_id:
            d=await message.reply_text(f"➕ **Already Added To Playlist!**")
            await mp.delete(d)
            await mp.delete(message)
            return
        data={1:m_audio.audio.title, 2:m_audio.audio.file_id, 3:"telegram", 4:user}
        playlist.append(data)
        if len(playlist) == 1:
            m_status = await message.reply_text("💞")
            await mp.download_audio(playlist[0])
            if 1 in RADIO:
                if group_call:
                    group_call.input_filename = ''
                    RADIO.remove(1)
                    RADIO.add(0)
                process = FFMPEG_PROCESSES.get
                if process:
                    try:
                        process.send_signal(SIGINT)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    except Exception as e:
                        print(e)
                        pass
                    FFMPEG_PROCESSES = ""
            if not group_call.is_connected:
                await mp.start_call()
            file=playlist[0][1]
            group_call.input_filename = os.path.join(
                _.workdir,
                DEFAULT_DOWNLOAD_DIR,
                f"{file}.raw"
            )
            await m_status.delete()
        if EDIT_TITLE:
            await mp.edit_title()
        if message.chat.type == "private":
            await message.reply_text(pl)            
        for track in playlist[:2]:
            await mp.download_audio(track)


    if type=="youtube" or type=="query":
        if type=="youtube":
            msg = await message.reply_text("🔍")
            url=yturl
        elif type=="query":
            try:
                msg = await message.reply_text("🔍")
                ytquery=ysearch
                results = YoutubeSearch(ytquery, max_results=1).to_dict()
                url = f"https://youtube.com{results[0]['url_suffix']}"
                title = results[0]["title"][:40]
            except Exception as e:
                await msg.edit(
                    "**Literary Found Noting!\nTry Searching On Inline 😉!**"
                )
                print(str(e))
                return
                await mp.delete(msg)
                await mp.delete(message)
        else:
            return
        ydl_opts = {
            "geo-bypass": True,
            "nocheckcertificate": True
        }
        ydl = YoutubeDL(ydl_opts)
        try:
            info = ydl.extract_info(url, False)
        except Exception as e:
            print(e)
            k=await msg.edit(
                f"❌ **YouTube Download Error !** \n\n{e}"
                )
            print(str(e))
            await mp.delete(message)
            await mp.delete(k)
            return
        duration = round(info["duration"] / 60)
        title= info["title"]
        if int(duration) > DURATION_LIMIT:
            k=await message.reply_text(f"❌ __Videos Longer Than {DURATION_LIMIT} Minute(s) Aren't Allowed, The Provided Video Is {duration} Minute(s)!__")
            await mp.delete(k)
            await mp.delete(message)
            return
        data={1:title, 2:url, 3:"youtube", 4:user}
        playlist.append(data)
        group_call = mp.group_call
        client = group_call.client
        if len(playlist) == 1:
            m_status = await msg.edit("💞")
            await mp.download_audio(playlist[0])
            if 1 in RADIO:
                if group_call:
                    group_call.input_filename = ''
                    RADIO.remove(1)
                    RADIO.add(0)
                process = FFMPEG_PROCESSES.get
                if process:
                    try:
                        process.send_signal(SIGINT)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    except Exception as e:
                        print(e)
                        pass
                    FFMPEG_PROCESSES = ""
            if not group_call.is_connected:
                await mp.start_call()
            file=playlist[0][1]
            group_call.input_filename = os.path.join(
                client.workdir,
                DEFAULT_DOWNLOAD_DIR,
                f"{file}.raw"
            )
            await m_status.delete()         
        if EDIT_TITLE:
            await mp.edit_title()      
        for track in playlist[:2]:
            await mp.download_audio(track)
    await mp.delete(message)

@Client.on_message(filters.command(["volume", f"volume@{USERNAME}"]) & ADMINS_FILTER & filters.private | filters.chat)
async def set_vol(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.ROBOT} **Didn't Joined Any Voice Chat!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    if len(m.command) < 2:
        k=await m.reply_text(f"{emoji.ROBOT} **You Forgot To Pass Volume (0-200)!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    await group_call.set_my_volume(int(m.command[1]))
    k=await m.reply_text(f"{emoji.SPEAKER_MEDIUM_VOLUME} **Volume Set To {m.command[1]}!**")
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["skip", f"skip@{USERNAME}"]) & ADMINS_FILTER & filters.private | filters.chat)
async def skip_track(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing To Skip!**")
        await mp.delete(k)
        await m.delete()
        return
    if len(m.command) == 1:
        await mp.skip_current_playing()                            
    else:
        try:
            items = list(dict.fromkeys(m.command[1:]))
            items = [int(x) for x in items if x.isdigit()]
            items.sort(reverse=True)
            text = []
            for i in items:
                if 2 <= i <= (len(playlist) - 1):
                    audio = f"{playlist[i][1]}"
                    playlist.pop(i)                                 
            k=await m.reply_text("\n".join(text))
            await mp.delete(k)
            if not playlist:
                pl = f"{emoji.NO_ENTRY} **Empty Playlist!**"        
            if m.chat.type == "private":
                await m.reply_text(pl)         

@Client.on_message(filters.command(["stop", f"stop@{USERNAME}"]) & ADMINS_FILTER & filters.private | filters.chat)
async def stop_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing To Stop!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    if 1 in RADIO:
        await mp.stop_radio()
    group_call.stop_playout()
    k=await m.reply_text(f"{emoji.STOP_BUTTON} **Stopped Playing!**")
    playlist.clear()
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["replay", f"replay@{USERNAME}"]) & ADMINS_FILTER & filters.private | filters.chat)
async def restart_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing To Replay!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    if not playlist:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Empty Playlist!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    group_call.restart_playout()
    k=await m.reply_text(
        f"{emoji.COUNTERCLOCKWISE_ARROWS_BUTTON}  "
        "**Playing From The Beginning!**"
    )
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["pause", f"pause@{USERNAME}"]) & ADMINS_FILTER & filters.private | filters.chat)
async def pause_playing(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing To Pause!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    mp.group_call.pause_playout()
    



@Client.on_message(filters.command(["resume", f"resume@{USERNAME}"]) & ADMINS_FILTER & filters.private | filters.chat)
async def resume_playing(_, m: Message):
    if not mp.group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Paused To Resume!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    mp.group_call.resume_playout()
    
@Client.on_message(filters.command(["clean", f"clean@{USERNAME}"]) & ADMINS_FILTER & filters.private | filters.chat)
async def clean_raw_pcm(client, m: Message):
    download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
    all_fn: list[str] = os.listdir(download_dir)
    for track in playlist[:2]:
        track_fn = f"{track[1]}.raw"
        if track_fn in all_fn:
            all_fn.remove(track_fn)
    count = 0
    if all_fn:
        for fn in all_fn:
            if fn.endswith(".raw"):
                count += 1
                os.remove(os.path.join(download_dir, fn))
    k=await m.reply_text(f"{emoji.WASTEBASKET} **Cleaned {count} Files!**")
    await mp.delete(k)
    await mp.delete(m)


@Client.on_message(filters.command(["mute", f"mute@{USERNAME}"]) & ADMINS_FILTER & filters.private | filters.chat)
async def mute(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Playing To Mute!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    await group_call.set_is_mute(True)
    

@Client.on_message(filters.command(["unmute", f"unmute@{USERNAME}"]) & ADMINS_FILTER & filters.private | filters.chat)
async def unmute(_, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        k=await m.reply_text(f"{emoji.NO_ENTRY} **Nothing Is Muted To Unmute!**")
        await mp.delete(k)
        await mp.delete(m)
        return
    await group_call.set_is_mute(False)
     
admincmds=["join", "unmute", "mute", "leave", "clean", "pause", "resume", "stop", "skip", "radio", "stopradio", "replay", "restart", "volume", f"volume@{USERNAME}", f"join@{USERNAME}", f"unmute@{USERNAME}", f"mute@{USERNAME}", f"leave@{USERNAME}", f"clean@{USERNAME}", f"pause@{USERNAME}", f"resume@{USERNAME}", f"stop@{USERNAME}", f"skip@{USERNAME}", f"radio@{USERNAME}", f"stopradio@{USERNAME}", f"replay@{USERNAME}", f"restart@{USERNAME}"]

@Client.on_message(filters.command(admincmds) & ADMINS_FILTER & filters.private | filters.chat)
async def notforu(_, m: Message):
    k=await m.reply_sticker("CAACAgUAAxkBAAEBpyZhF4R-ZbS5HUrOxI_MSQ10hQt65QACcAMAApOsoVSPUT5eqj5H0h4E")
    await mp.delete(k)
    await mp.delete(m)

allcmd = ["play", "current", "playlist", "song", f"song@{USERNAME}", f"play@{USERNAME}", f"current@{USERNAME}", f"playlist@{USERNAME}"] + admincmds

@Client.on_message(filters.command(allcmd) & filters.group & ~filters.chat(CHAT_ID) & ~filters.chat(LOG_GROUP))
async def not_chat(_, m: Message):
    buttons = [
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/DC_LOGS"),
                InlineKeyboardButton("SUPPORT", url="https://t.me/DC_Kurukshethra"),
            ],          
         ]
    k=await m.reply_photo(photo="http://telegra.ph/file/bdf2ee8348572a65cc311.jpg", caption="**Sorry, You Can't Use This Bot In This Group! 🤷‍♂️ But You Can Make Your Own Bot Like This From The [Source Code](https://github.com/AsmSafone/RadioPlayerV3) Below 😉!**", reply_markup=InlineKeyboardMarkup(buttons))
    await mp.delete(m)
