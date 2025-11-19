import discord
import os
import sys

# Get Discord token from environment variable
TOKEN = os.getenv('DISCORD_TOKEN')

# Check if token exists
if not TOKEN:
    print('❌ ERROR: DISCORD_TOKEN environment variable not found!')
    sys.exit(1)

# Setup bot with minimal intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot client
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    """Bot startup event"""
    print('='*50)
    print(f'✅ Bot is now ONLINE!')
    print(f'Bot Name: {client.user.name}')
    print(f'Bot ID: {client.user.id}')
    print('='*50)
    print('Bot is ready to receive commands!')

@client.event
async def on_message(message):
    """Handle incoming messages"""
    
    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    # Ping command - Test if bot is responsive
    if message.content.lower() == '!ping':
        await message.channel.send('🏓 **Pong!** Bot is online and working!')
    
    # Info command - Show bot information
    elif message.content.lower() == '!info':
        embed = discord.Embed(
            title='🍃 Konoha Bot',
            description='Discord bot for community management',
            color=0x00ff00
        )
        embed.add_field(name='Server', value=message.guild.name, inline=True)
        embed.add_field(name='Members', value=message.guild.member_count, inline=True)
        embed.add_field(name='Status', value='✅ Online', inline=True)
        embed.set_footer(text=f'Requested by {message.author.name}')
        await message.channel.send(embed=embed)
    
    # Help command - Show available commands
    elif message.content.lower() == '!help':
        help_text = """
**📚 Available Commands:**

`!ping` - Test if bot is online
`!info` - Show bot and server information
`!help` - Display this help message

**Bot Prefix:** `!`
**Status:** Online ✅
        """
        await message.channel.send(help_text)

# Run the bot
try:
    print('Starting bot...')
    client.run(TOKEN)
except Exception as e:
    print(f'❌ Error running bot: {e}')
    sys.exit(1)
