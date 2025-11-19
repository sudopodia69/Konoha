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
    print('='*50)
    print(f'✅ Bot is now ONLINE!')
    print(f'Bot Name: {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('='*50)

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
            await ctx.send(f'✅ {member.name} is now an admin!')
        else:
            await ctx.send(f'⚠️ Already admin!')
    else:
        await ctx.send('❌ Owner only!')

@bot.command()
async def removeadmin(ctx, member: discord.Member):
    if ctx.author.id == ctx.guild.owner_id:
        if str(member.id) in db['admins']:
            db['admins'].remove(str(member.id))
            save_database(db)
            await ctx.send(f'✅ Removed!')
        else:
            await ctx.send(f'⚠️ Not admin!')
    else:
        await ctx.send('❌ Owner only!')

@bot.command()
async def addresponse(ctx, task_id: str, *, response_text: str):
    if not is_admin(ctx.author.id):
        await ctx.send('❌ Admin only!')
        return
    db['responses'][task_id] = response_text
    save_database(db)
    await ctx.send(f'✅ Added: {task_id}')

@bot.command()
async def removeresponse(ctx, task_id: str):
    if not is_admin(ctx.author.id):
        await ctx.send('❌ Admin only!')
        return
    if task_id in db['responses']:
        del db['responses'][task_id]
        save_database(db)
        await ctx.send(f'✅ Removed: {task_id}')
    else:
        await ctx.send(f'❌ Not found!')

@bot.command()
async def editresponse(ctx, task_id: str, *, new_text: str):
    if not is_admin(ctx.author.id):
        await ctx.send('❌ Admin only!')
        return
    if task_id in db['responses']:
        db['responses'][task_id] = new_text
        save_database(db)
        await ctx.send(f'✅ Updated: {task_id}')
    else:
        await ctx.send(f'❌ Not found!')

@bot.command()
async def listresponses(ctx):
    if not is_admin(ctx.author.id):
        await ctx.send('❌ Admin only!')
        return
    if not db['responses']:
        await ctx.send('No responses!')
        return
    text = '
'.join([f'{k}: {v[:50]}...' if len(v) > 50 else f'{k}: {v}' for k, v in db['responses'].items()])
    await ctx.send(f'**Responses ({len(db["responses"])}):**
{text}')

@bot.command()
async def setchannel(ctx, channel: discord.TextChannel):
    if not is_admin(ctx.author.id):
        await ctx.send('❌ Admin only!')
        return
    channel_id = str(channel.id)
    if channel_id not in db['channels']:
        db['channels'].append(channel_id)
        save_database(db)
        await ctx.send(f'✅ Enabled in {channel.mention}')
    else:
        await ctx.send(f'⚠️ Already enabled!')

@bot.command()
async def removechannel(ctx, channel: discord.TextChannel):
    if not is_admin(ctx.author.id):
        await ctx.send('❌ Admin only!')
        return
    channel_id = str(channel.id)
    if channel_id in db['channels']:
        db['channels'].remove(channel_id)
        save_database(db)
        await ctx.send(f'✅ Disabled in {channel.mention}')
    else:
        await ctx.send(f'⚠️ Not enabled!')

@bot.command()
async def stats(ctx, member: discord.Member = None):
    target = member or ctx.author
    user_id = str(target.id)
    if user_id not in db['stats']:
        await ctx.send(f'{target.name} has no stats!')
        return
    s = db['stats'][user_id]
    stats_text = f"""**{target.name} Statistics:**
Searches Today: {s['searches_today']}
Total Searches: {s['total_searches']}
Last Search: {s['last_search'] if s['last_search'] else 'Never'}"""
    await ctx.send(stats_text)

@bot.command()
async def leaderboard(ctx):
    if not db['stats']:
        await ctx.send('No stats yet!')
        return
    sorted_users = sorted(db['stats'].items(), key=lambda x: x[1]['total_searches'], reverse=True)[:10]
    text = '**🏆 Top Searchers:**
'
    for i, (uid, data) in enumerate(sorted_users, 1):
        member = ctx.guild.get_member(int(uid))
        name = member.name if member else f'User {uid}'
        text += f'{i}. {name}: {data["total_searches"]} searches
'
    await ctx.send(text)

@bot.command()
async def givemembership(ctx, member: discord.Member, days: int):
    if not is_admin(ctx.author.id):
        await ctx.send('❌ Admin only!')
        return
    user_id = str(member.id)
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    db['subscriptions'][user_id] = {
        'start_date': datetime.now().isoformat(),
        'expiry_date': expiry,
        'days': days,
        'active': True
    }
    save_database(db)
    await ctx.send(f'✅ Premium granted to {member.mention} for {days} days!')

@bot.command()
async def subscription(ctx):
    user_id = str(ctx.author.id)
    if user_id not in db['subscriptions']:
        await ctx.send('No active subscription!')
        return
    sub = db['subscriptions'][user_id]
    expiry = datetime.fromisoformat(sub['expiry_date'])
    days_left = (expiry - datetime.now()).days
    status_text = f"""**Your Subscription:**
Status: {'✅ Active' if sub['active'] else '❌ Expired'}
Expires: {expiry.strftime('%Y-%m-%d')}
Days Left: {days_left}"""
    await ctx.send(status_text)

@bot.command()
async def listpremium(ctx):
    if not is_admin(ctx.author.id):
        await ctx.send('❌ Admin only!')
        return
    if not db['subscriptions']:
        await ctx.send('No premium members!')
        return
    premium_list = ''
    for user_id, sub in db['subscriptions'].items():
        member = ctx.guild.get_member(int(user_id))
        name = member.name if member else f'User {user_id}'
        expiry = datetime.fromisoformat(sub['expiry_date'])
        days_left = (expiry - datetime.now()).days
        premium_list += f'{name}: {days_left} days
'
    await ctx.send(f'**Premium Members:**
{premium_list}')

@bot.command()
async def ping(ctx):
    await ctx.send('🏓 Pong! Bot online!')

@bot.command()
async def info(ctx):
    info_text = f"""**Bot Info:**
Responses: {len(db['responses'])}
Users Tracked: {len(db['stats'])}
Premium Members: {len(db['subscriptions'])}
Servers: {len(bot.guilds)}"""
    await ctx.send(info_text)

@bot.command()
async def help(ctx):
    help_text = """**Commands:**

**Basic:**
!ping - Test
!info - Bot info
!help - This message

**Autoresponder (Admin):**
!addresponse <id> <text>
!removeresponse <id>
!editresponse <id> <text>
!listresponses
!setchannel #channel
!removechannel #channel

**Stats:**
!stats [@user]
!leaderboard

**Subscription (Admin):**
!givemembership @user <days>
!subscription
!listpremium

**Admin:**
!setadmin @user
!removeadmin @user"""
    await ctx.send(help_text)

if TOKEN:
    bot.run(TOKEN)
else:
    print('❌ TOKEN not found!')
