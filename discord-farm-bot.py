import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Time zones setup
gmt = pytz.timezone('GMT')
gmt_plus_2 = pytz.timezone('Europe/Kiev')  # Using Kiev as it's GMT+2

# Define check times for each category
TREES_MUSHROOMS = [
    "1:37", "2:17", "2:57", "3:37", "4:17", "4:57", "5:37", "6:17", "6:57",
    "7:37", "8:17", "8:57", "9:37", "10:17", "10:57", "11:37", "12:17", "12:57",
    "13:37", "14:17", "14:57", "15:37", "16:17", "16:57", "17:37", "18:17", "18:57",
    "19:37", "20:17", "20:57", "21:37", "22:17", "22:57", "23:37", "0:17", "0:57"
]

FRUIT_TREES = [
    "1:37", "4:17", "6:57", "9:37", "12:17", "14:57", "17:37", "20:17", "22:57"
]

HARDWOOD_CYCLES = {
    1: ["1:37", "12:17", "22:57"],
    2: ["9:37", "20:17"],
    3: ["6:57", "17:37"],
    4: ["4:17", "14:57"]
}

HERBS_BUSHES = ["0:17", "0:37", "0:57", "1:17", "1:37", "1:57", "2:17", "2:37", "2:57",
                "3:17", "3:37", "3:57", "4:17", "4:37", "4:57", "5:17", "5:37", "5:57",
                "6:17", "6:37", "6:57", "7:17", "7:37", "7:57", "8:17", "8:37", "8:57",
                "9:17", "9:37", "9:57", "10:17", "10:37", "10:57", "11:17", "11:37", "11:57",
                "12:17", "12:37", "12:57", "13:17", "13:37", "13:57", "14:17", "14:37", "14:57",
                "15:17", "15:37", "15:57", "16:17", "16:37", "16:57", "17:17", "17:37", "17:57",
                "18:17", "18:37", "18:57", "19:17", "19:37", "19:57", "20:17", "20:37", "20:57",
                "21:17", "21:37", "21:57", "22:17", "22:37", "22:57", "23:17", "23:37", "23:57"]

# Channel ID to send notifications (you'll need to set this)
NOTIFICATION_CHANNEL_ID = None
# Current day in the hardwood cycle (1-4)
current_hardwood_day = 1

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    check_times.start()

@tasks.loop(minutes=1)
async def check_times():
    if NOTIFICATION_CHANNEL_ID is None:
        return
        
    channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
    if not channel:
        return

    current_time = datetime.now(gmt_plus_2)
    time_str = current_time.strftime("%H:%M")

    # Check Trees/Mushrooms
    if time_str in TREES_MUSHROOMS:
        await channel.send("🌳 **Trees and Mushrooms** are ready to be checked!")

    # Check Fruit Trees
    if time_str in FRUIT_TREES:
        await channel.send("🍎 **Fruit Trees, Calquat, and Celastrus** are ready to be checked!")

    # Check Hardwoods based on current day
    if time_str in HARDWOOD_CYCLES[current_hardwood_day]:
        await channel.send(f"🌲 **Hardwoods, Redwood, Anima, Hespori** (Day {current_hardwood_day}) are ready to be checked!")

    # Check Herbs/Bushes
    if time_str in HERBS_BUSHES:
        await channel.send("🌿 **Herbs and Bushes** are ready to be checked!")

@bot.command(name='setchannel')
@commands.has_permissions(administrator=True)
async def set_notification_channel(ctx):
    """Sets the current channel as the notification channel"""
    global NOTIFICATION_CHANNEL_ID
    NOTIFICATION_CHANNEL_ID = ctx.channel.id
    await ctx.send(f"Notification channel set to: {ctx.channel.name}")

@bot.command(name='sethardwoodday')
@commands.has_permissions(administrator=True)
async def set_hardwood_day(ctx, day: int):
    """Sets the current day in the hardwood cycle (1-4)"""
    global current_hardwood_day
    if 1 <= day <= 4:
        current_hardwood_day = day
        await ctx.send(f"Hardwood cycle day set to: {day}")
    else:
        await ctx.send("Please provide a day between 1 and 4")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")

# Replace 'YOUR_BOT_TOKEN' with your actual Discord bot token
bot.run('YOUR_BOT_TOKEN')
