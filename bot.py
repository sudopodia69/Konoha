import discord
import os

# Get token from environment
TOKEN = os.getenv('DISCORD_TOKEN')

# Simple client setup
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'✅ {client.user} is now online!')
    print('Bot ready!')

@client.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == client.user:
        return
    
    # Ping command
    if message.content == '!ping':
        await message.channel.send('🏓 Pong! Bot is working!')
    
    # Info command
    if message.content == '!info':
        await message.channel.send(f'🍃 Konoha Bot
Server: {message.guild.name}
Status: Online ✅')
    
    # Help command
    if message.content == '!help':
        await message.channel.send('**Commands:**
!ping - Test bot
!info - Bot info
!help - This message')

# Run bot
if TOKEN:
    client.run(TOKEN)
else:
    print('❌ TOKEN not found!')
