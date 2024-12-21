from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from discord.ext import commands
from responses import get_response
import discord
import yt_dlp



#load token
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

#bot setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents, command_prefix = "!")


#message functionality
async def send_message(message: Message, user_message: str ) -> None:
    if not user_message:
        print("message empty")
        return
    
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


#startup
@client.event
async def on_ready():
    print(f"{client.user} has started running")



# Track voice channel for playing
voice_channel = None

async def play_audio(url):
    try:
        # Check if connected to a voice channel
        if not voice_channel:
            print("Bot is not connected to a voice channel.")
            return

        with yt_dlp.YoutubeDL({'format': 'bestaudio/best'}) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        print(URL)

        source = await discord.FFmpegOpusAudio.from_probe(URL)

        voice_client = voice_channel.guild.voice_client
        if voice_client:
            voice_client.play(source, after=lambda e: print(f"Audio finished playing: {e}"))  # Handle audio finish event
            await voice_client.channel.send(f"Now playing: {info['title']}")
        else:
            print("Bot is not connected to a voice channel.")
    except Exception as e:
        print(f"An error occurred while playing: {e}") 
        if voice_client and voice_client.is_playing():
            voice_client.stop()

async def join(ctx):
    """Joins the voice channel you're currently in."""
    if ctx.author.voice is None:
        await ctx.send("You are not connected to a voice channel.")
    else:
        channel = ctx.author.voice.channel
        try:
            await channel.connect()
            voice_channel = channel  # Update global or class-level voice_channel (explained below)
            print(f"Joined voice channel: {channel}")
        except Exception as e:
            await ctx.send(f"Failed to join voice channel: {e}")



# Listen for voice state updates
@client.event
async def on_voice_state_update(member, before, after):
    global voice_channel
    # Check if bot joined or left a voice channel
    if not member.guild.voice_client:
        return

    if not before.channel and after.channel:
        voice_channel = after.channel
        print(f"Bot joined voice channel: {voice_channel}")
    elif before.channel and not after.channel:
        voice_channel = None
        print(f"Bot left voice channel")

# Message processing
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username = str(message.author)
    user_message = message.content
    channel = str(message.channel)

    print(f"[{channel}] {username}: '{user_message}'")

    # Manual command parsing for playing
    if user_message.startswith('!play'):
        url = user_message[6:]  # Extract URL after "!play"
        await play_audio(url=url)

    elif user_message.startswith('!join'):
        await join(message)






#main
def main():
    client.run(token=TOKEN)
    

if __name__ == "__main__":
    main()