import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta

TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
DATABASE_FILE = 'database.json'

def load_database():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    return {"responses": {}, "admins": [], "channels": [], "stats": {}, "subscriptions": {}}

def save_database(data):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_database()

def is_admin(user_id):
    return str(user_id) in db['admins']

@bot.event
async def on_ready():
    print('Bot is now ONLINE!')
    print(f'Name: {bot.user.name}')
    print(f'ID: {bot.user.id}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)
    if message.content.isdigit():
        task_id = message.content
        if db['channels'] and str(message.channel.id) not in db['channels']:
            return
        if task_id in db['responses']:
            await message.channel.send(db['responses'][task_id])
            user_id = str(message.author.id)
            if user_id not in db['stats']:
                db['stats'][user_id] = {'searches_today': 0, 'total_searches': 0, 'last_search': None}
            db['stats'][user_id]['searches_today'] += 1
            db['stats'][user_id]['total_searches'] += 1
            db['stats'][user_id]['last_search'] = datetime.now().isoformat()
            save_database(db)

@bot.command()
async def setadmin(ctx, member: discord.Member):
    if ctx.author.id == ctx.guild.owner_id:
        if str(member.id) not in db['admins']:
            db['admins'].append(str(member.id))
            save_database(db)
            await ctx.send(f'Admin added: {member.name}')
        else:
            await ctx.send('Already admin!')
    else:
        await ctx.send('Owner only!')

@bot.command()
async def addresponse(ctx, task_id: str, *, response_text: str):
    if not is_admin(ctx.author.id):
        await ctx.send('Admin only!')
        return
    db['responses'][task_id] = response_text
    save_database(db)
    await ctx.send(f'Added: {task_id}')

@bot.command()
async def removeresponse(ctx, task_id: str):
    if not is_admin(ctx.author.id):
        await ctx.send('Admin only!')
        return
    if task_id in db['responses']:
        del db['responses'][task_id]
        save_database(db)
        await ctx.send(f'Removed: {task_id}')

@bot.command()
async def listresponses(ctx):
    if not is_admin(ctx.author.id):
        await ctx.send('Admin only!')
        return
    if not db['responses']:
        await ctx.send('No responses!')
        return
    text = '
'.join([f'{k}: {v[:30]}' for k, v in db['responses'].items()])
    await ctx.send(f'Responses:
{text}')

@bot.command()
async def setchannel(ctx, channel: discord.TextChannel):
    if not is_admin(ctx.author.id):
        await ctx.send('Admin only!')
        return
    channel_id = str(channel.id)
    if channel_id not in db['channels']:
        db['channels'].append(channel_id)
        save_database(db)
        await ctx.send(f'Channel enabled')

@bot.command()
async def stats(ctx, member: discord.Member = None):
    target = member or ctx.author
    user_id = str(target.id)
    if user_id not in db['stats']:
        await ctx.send('No stats!')
        return
    s = db['stats'][user_id]
    await ctx.send(f'{target.name}
Today: {s["searches_today"]}
Total: {s["total_searches"]}')

@bot.command()
async def givemembership(ctx, member: discord.Member, days: int):
    if not is_admin(ctx.author.id):
        await ctx.send('Admin only!')
        return
    user_id = str(member.id)
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    db['subscriptions'][user_id] = {'expiry_date': expiry, 'days': days, 'active': True}
    save_database(db)
    await ctx.send(f'Premium granted for {days} days!')

@bot.command()
async def subscription(ctx):
    user_id = str(ctx.author.id)
    if user_id not in db['subscriptions']:
        await ctx.send('No subscription!')
        return
    sub = db['subscriptions'][user_id]
    expiry = datetime.fromisoformat(sub['expiry_date'])
    days_left = (expiry - datetime.now()).days
    await ctx.send(f'Expires: {expiry.strftime("%Y-%m-%d")}
Days left: {days_left}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def help(ctx):
    await ctx.send('Commands: !ping !addresponse !listresponses !stats !givemembership !subscription !setadmin !setchannel')

if TOKEN:
    bot.run(TOKEN)
else:
    print('No TOKEN!')
