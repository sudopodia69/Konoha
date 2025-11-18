import discord
from discord.ext import commands
import os

# Bot token from environment variable
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Event: Bot ready
@bot.event
async def on_ready():
    print(f'✅ {bot.user} is now online!')
    print(f'Bot ID: {bot.user.id}')
    print('Ready to serve!')

# Command: Test if bot is working
@bot.command()
async def ping(ctx):
    """Check if bot is responding"""
    await ctx.send(f'🏓 Pong! Bot is online and working!')

# Command: Bot info
@bot.command()
async def info(ctx):
    """Show bot information"""
    embed = discord.Embed(
        title="🤖 JumpTask Bot",
        description="Advanced Discord bot for JumpTask community",
        color=0x00ff00
    )
    embed.add_field(name="Prefix", value="!", inline=True)
    embed.add_field(name="Server", value=ctx.guild.name, inline=True)
    await ctx.send(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `!help` for available commands.")
    else:
        print(f'Error: {error}')

# Run bot
if __name__ == "__main__":
    if TOKEN is None:
        print("❌ ERROR: DISCORD_TOKEN not found in environment variables!")
    else:
        bot.run(TOKEN)
