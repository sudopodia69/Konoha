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

def load_db():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    return {"responses": {}, "admins": [], "channels": [], "stats": {}, "subs": {}}

def save_db(data):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

db = load_db()

def is_admin(uid):
    return str(uid) in db['admins']

@bot.event
async def on_ready():
    print('Bot online!')
    print(f'Name: {bot.user.name}')

@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    await bot.process_commands(msg)
    if msg.content.isdigit():
        tid = msg.content
        if db['channels'] and str(msg.channel.id) not in db['channels']:
            return
        if tid in db['responses']:
            await msg.channel.send(db['responses'][tid])
            uid = str(msg.author.id)
            if uid not in db['stats']:
                db['stats'][uid] = {'today': 0, 'total': 0}
            db['stats'][uid]['today'] += 1
            db['stats'][uid]['total'] += 1
            save_db(db)

@bot.command()
async def setadmin(ctx, member: discord.Member):
    if ctx.author.id == ctx.guild.owner_id:
        if str(member.id) not in db['admins']:
            db['admins'].append(str(member.id))
            save_db(db)
            await ctx.send(f'Added: {member.name}')
        else:
            await ctx.send('Already admin')
    else:
        await ctx.send('Owner only')

@bot.command()
async def add(ctx, tid: str, *, text: str):
    if not is_admin(ctx.author.id):
        await ctx.send('Admin only')
        return
    db['responses'][tid] = text
    save_db(db)
    await ctx.send(f'Added: {tid}')

@bot.command()
async def remove(ctx, tid: str):
    if not is_admin(ctx.author.id):
        await ctx.send('Admin only')
        return
    if tid in db['responses']:
        del db['responses'][tid]
        save_db(db)
        await ctx.send(f'Removed: {tid}')
    else:
        await ctx.send('Not found')

@bot.command()
async def edit(ctx, tid: str, *, text: str):
    if not is_admin(ctx.author.id):
        await ctx.send('Admin only')
        return
    if tid in db['responses']:
        db['responses'][tid] = text
        save_db(db)
        await ctx.send(f'Updated: {tid}')
    else:
        await ctx.send('Not found')

@bot.command()
async def list(ctx):
    if not is_admin(ctx.author.id):
        await ctx.send('Admin only')
        return
    if not db['responses']:
        await ctx.send('Empty')
        return
    text = '
'.join([f'{k}: {v[:30]}' for k, v in db['responses'].items()])
    await ctx.send(f'Responses:
{text}')

@bot.command()
async def setchannel(ctx, ch: discord.TextChannel):
    if not is_admin(ctx.author.id):
        await ctx.send('Admin only')
        return
    cid = str(ch.id)
    if cid not in db['channels']:
        db['channels'].append(cid)
        save_db(db)
        await ctx.send(f'Enabled in {ch.mention}')
    else:
        await ctx.send('Already enabled')

@bot.command()
async def stats(ctx, member: discord.Member = None):
    target = member or ctx.author
    uid = str(target.id)
    if uid not in db['stats']:
        await ctx.send('No stats')
        return
    s = db['stats'][uid]
    await ctx.send(f'{target.name}
Today: {s["today"]}
Total: {s["total"]}')

@bot.command()
async def leaderboard(ctx):
    if not db['stats']:
        await ctx.send('No stats')
        return
    sorted_users = sorted(db['stats'].items(), key=lambda x: x[1]['total'], reverse=True)[:10]
    text = 'Top Users:
'
    for i, (uid, data) in enumerate(sorted_users, 1):
        member = ctx.guild.get_member(int(uid))
        name = member.name if member else f'User{uid}'
        text += f'{i}. {name}: {data["total"]}
'
    await ctx.send(text)

@bot.command()
async def give(ctx, member: discord.Member, days: int):
    if not is_admin(ctx.author.id):
        await ctx.send('Admin only')
        return
    uid = str(member.id)
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    db['subs'][uid] = {'expiry': expiry, 'days': days}
    save_db(db)
    await ctx.send(f'Premium: {days} days for {member.mention}')

@bot.command()
async def sub(ctx):
    uid = str(ctx.author.id)
    if uid not in db['subs']:
        await ctx.send('No subscription')
        return
    s = db['subs'][uid]
    expiry = datetime.fromisoformat(s['expiry'])
    left = (expiry - datetime.now()).days
    await ctx.send(f'Expires: {expiry.strftime("%Y-%m-%d")}
Days left: {left}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def help(ctx):
    cmds = '''Commands:
!ping - Test
!add <id> <text> - Add response (admin)
!remove <id> - Remove (admin)
!edit <id> <text> - Edit (admin)
!list - List all (admin)
!setchannel #channel - Set channel (admin)
!stats [@user] - View stats
!leaderboard - Top users
!give @user <days> - Premium (admin)
!sub - Your subscription
!setadmin @user - Make admin (owner)'''
    await ctx.send(cmds)

if TOKEN:
    bot.run(TOKEN)
else:
    print('No TOKEN')
