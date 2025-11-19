import discord
import os
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client(intents=discord.Intents.default())
@client.event
async def on_ready():
    print('Bot online!')
@client.event  
async def on_message(message):
    if message.author.bot:
        return
    if message.content == '!ping':
        await message.channel.send('Pong!')
if TOKEN:
    client.run(TOKEN)
