import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz
import os

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

# Channel ID to store notification channel IDs (multiple servers can use the bot)
notification_channels = {}
# Current day in the hardwood cycle (1-4) for each server
hardwood_days = {}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    check_times.start()

@tasks.loop(minutes=1)
async def check_times():
    current_time = datetime.now(gmt_plus_2)
    time_str = current_time.strftime("%H:%M")
    
    # Check if it's midnight to update hardwood day
    if time_str == "00:00":
        for guild_id in hardwood_days.keys():
            current_day = hardwood_days[guild_id]
            # Update to next day (1->2->3->4->1)
            hardwood_days[guild_id] = current_day % 4 + 1
            
            # Get channel to announce day change
            channel_id = notification_channels.get(guild_id)
            if channel_id:
                channel = bot.get_channel(channel_id)
                if channel:
                    await channel.send(f"🌲 Hardwood day has automatically updated to Day {hardwood_days[guild_id]}")

    # Check each registered channel
    for guild_id, channel_id in notification_channels.items():
        channel = bot.get_channel(channel_id)
        if not channel:
            continue

        current_day = hardwood_days.get(guild_id, 1)

        # Check Trees/Mushrooms
        if time_str in TREES_MUSHROOMS:
            await channel.send("🌳 **Trees and Mushrooms** are ready to be checked!")

        # Check Fruit Trees
        if time_str in FRUIT_TREES:
            await channel.send("🍎 **Fruit Trees, Calquat, and Celastrus** are ready to be checked!")

        # Check Hardwoods based on current day
        if time_str in HARDWOOD_CYCLES[current_day]:
            await channel.send(f"🌲 **Hardwoods, Redwood, Anima, Hespori** (Day {current_day}) are ready to be checked!")

        # Check Herbs/Bushes
        if time_str in HERBS_BUSHES:
            await channel.send("🌿 **Herbs and Bushes** are ready to be checked!")

@bot.command(name='setchannel')
@commands.has_permissions(administrator=True)
async def set_notification_channel(ctx):
    """Sets the current channel as the notification channel for this server"""
    notification_channels[ctx.guild.id] = ctx.channel.id
    await ctx.send(f"Notification channel set to: {ctx.channel.name}")

@bot.command(name='sethardwoodday')
@commands.has_permissions(administrator=True)
async def set_hardwood_day(ctx, day: int):
    """Sets the current day in the hardwood cycle (1-4) for this server"""
    if 1 <= day <= 4:
        hardwood_days[ctx.guild.id] = day
        await ctx.send(f"Hardwood cycle day set to: {day}")
    else:
        await ctx.send("Please provide a day between 1 and 4")

@bot.command(name='status')
async def check_status(ctx):
    """Check the current status of the bot for this server"""
    channel_id = notification_channels.get(ctx.guild.id)
    day = hardwood_days.get(ctx.guild.id)
    
    if channel_id:
        channel = bot.get_channel(channel_id)
        await ctx.send(f"Notifications are set to: {channel.mention}")
    else:
        await ctx.send("No notification channel set! Use !setchannel to set one.")
    
    if day:
        await ctx.send(f"Current hardwood day: {day}")
    else:
        await ctx.send("No hardwood day set! Use !sethardwoodday to set one.")

def get_next_times(current_time_str, times_list, count=1):
    """Get the next N times from a list of times"""
    # Convert all times to minutes for easier comparison
    current_hours, current_minutes = map(int, current_time_str.split(':'))
    current_total_minutes = current_hours * 60 + current_minutes
    
    # Convert time strings to minutes
    times_in_minutes = []
    for time_str in times_list:
        hours, minutes = map(int, time_str.split(':'))
        total_minutes = hours * 60 + minutes
        times_in_minutes.append((total_minutes, time_str))
    
    # Sort times
    times_in_minutes.sort()
    
    # Find next times
    next_times = []
    for _ in range(count):
        found = False
        for minutes, time_str in times_in_minutes:
            if minutes > current_total_minutes:
                next_times.append(time_str)
                found = True
                break
        if not found and times_in_minutes:  # If not found, take from start of next day
            next_times.append(times_in_minutes[0][1])
        current_total_minutes = int(next_times[-1].split(':')[0]) * 60 + int(next_times[-1].split(':')[1])
    
    return next_times

@bot.command(name='next')
async def next_times(ctx):
    """Show next farming time for each category"""
    current_time = datetime.now(gmt_plus_2)
    current_time_str = current_time.strftime("%H:%M")
    
    embed = discord.Embed(title="Next Farming Times", color=0x00ff00)
    
    # Trees and Mushrooms
    next_tree = get_next_times(current_time_str, TREES_MUSHROOMS)[0]
    embed.add_field(name="🌳 Trees & Mushrooms", value=f"Next: {next_tree}", inline=False)
    
    # Fruit Trees
    next_fruit = get_next_times(current_time_str, FRUIT_TREES)[0]
    embed.add_field(name="🍎 Fruit Trees, Calquat, Celastrus", value=f"Next: {next_fruit}", inline=False)
    
    # Hardwoods
    current_day = hardwood_days.get(ctx.guild.id, 1)
    next_hardwood = get_next_times(current_time_str, HARDWOOD_CYCLES[current_day])[0]
    embed.add_field(name=f"🌲 Hardwoods (Day {current_day})", value=f"Next: {next_hardwood}", inline=False)
    
    # Herbs and Bushes
    next_herb = get_next_times(current_time_str, HERBS_BUSHES)[0]
    embed.add_field(name="🌿 Herbs & Bushes", value=f"Next: {next_herb}", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='next5')
async def next_five_times(ctx):
    """Show next 5 farming times for each category"""
    current_time = datetime.now(gmt_plus_2)
    current_time_str = current_time.strftime("%H:%M")
    
    embed = discord.Embed(title="Next 5 Farming Times", color=0x00ff00)
    
    # Trees and Mushrooms
    next_trees = get_next_times(current_time_str, TREES_MUSHROOMS, 5)
    embed.add_field(name="🌳 Trees & Mushrooms", value="\n".join(next_trees), inline=False)
    
    # Fruit Trees
    next_fruits = get_next_times(current_time_str, FRUIT_TREES, 5)
    embed.add_field(name="🍎 Fruit Trees, Calquat, Celastrus", value="\n".join(next_fruits), inline=False)
    
    # Hardwoods
    current_day = hardwood_days.get(ctx.guild.id, 1)
    next_hardwoods = get_next_times(current_time_str, HARDWOOD_CYCLES[current_day], 5)
    embed.add_field(name=f"🌲 Hardwoods (Day {current_day})", value="\n".join(next_hardwoods), inline=False)
    
    # Herbs and Bushes
    next_herbs = get_next_times(current_time_str, HERBS_BUSHES, 5)
    embed.add_field(name="🌿 Herbs & Bushes", value="\n".join(next_herbs), inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='times')
async def show_category_times(ctx, category: str):
    """Show all times for a specific category"""
    category = category.lower()
    embed = discord.Embed(color=0x00ff00)
    
    if category in ['trees', 'tree', 'mushroom', 'mushrooms']:
        embed.title = "🌳 Trees & Mushrooms Times"
        times_list = TREES_MUSHROOMS
    elif category in ['fruit', 'fruittrees', 'calquat', 'celastrus']:
        embed.title = "🍎 Fruit Trees, Calquat, Celastrus Times"
        times_list = FRUIT_TREES
    elif category in ['hardwood', 'hardwoods', 'redwood', 'anima', 'hespori']:
        current_day = hardwood_days.get(ctx.guild.id, 1)
        embed.title = f"🌲 Hardwoods Times (Day {current_day})"
        times_list = HARDWOOD_CYCLES[current_day]
    elif category in ['herbs', 'herb', 'bush', 'bushes']:
        embed.title = "🌿 Herbs & Bushes Times"
        times_list = HERBS_BUSHES
    else:
        await ctx.send("Invalid category. Valid categories are: trees, fruit, hardwood, herbs")
        return
    
    # Sort times for display
    sorted_times = sorted(times_list, key=lambda x: tuple(map(int, x.split(':'))))
    
    # Split into multiple fields if needed (Discord has a 1024 character limit per field)
    times_str = ""
    for time in sorted_times:
        if len(times_str) + len(time) + 2 > 1024:  # +2 for the newline
            embed.add_field(name="Times", value=times_str, inline=False)
            times_str = time + "\n"
        else:
            times_str += time + "\n"
    
    if times_str:
        embed.add_field(name="Times", value=times_str, inline=False)
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

# Get the token from environment variable
bot.run(os.getenv('DISCORD_TOKEN'))
