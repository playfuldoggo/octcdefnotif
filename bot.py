import datetime
import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
import os
import json
from dotenv import load_dotenv
import re
load_dotenv()  # This will load the .env file and make the token accessible

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent for reading messages

# Initialize bot with intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Store the MOTD in a file (in memory or a file-based approach)
motd_data_file = 'motd_data.json'
minecraft_server_ip = "play.oc.tc"  # Your Minecraft server IP

def load_map():
    """Load the current map from the file."""
    try:
        with open(motd_data_file, 'r') as file:
            data = json.load(file)
            # Ensure the data is a list
            if isinstance(data, dict):  # If data is a dictionary, convert it to a list
                data = [data]
            elif not isinstance(data, list):  # If data is not a list, reset to an empty list
                data = []
    except (FileNotFoundError, json.JSONDecodeError):
        data = []  # Return an empty list if the file doesn't exist or is corrupted
    return data

def save_mapname(mapname, names, status):
    global timeonmap
    global saved_mapname
    saved_mapname = mapname
    """Save the mapname to the file."""
    data = load_map()
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    new_data = {"map name": mapname, "map time": timeonmap, "date": current_date, "online": status.players.online, "names": names}
    data.append(new_data)  # Add the new map data as an entry to the list
    
    with open(motd_data_file, 'w') as file:
        json.dump(data, file, indent=4)

def update_minutes(minutes):
    global timeonmap
    data = load_map()
    if data:  # Check if there's at least one entry in the data
        # Update the "map time" of the most recent entry
        data[-1]['map time'] = minutes
        with open(motd_data_file, 'w') as file:
            json.dump(data, file, indent=4)

async def get_motd_from_server():
    """Fetch the MOTD from the Minecraft server."""
    try:
        server = JavaServer.lookup(minecraft_server_ip)
        status = server.status()
        return status
    except Exception as e:
        print(f"Error fetching MOTD: {e}")
        return None

# Define the channel ID where the message will be sent
CHANNEL_ID = 708041597408772167  # Replace with your Discord channel ID
timeonmap = 0
pattern = "§r§r§4Overcast §r§7Community§r\n§r§r§(.)»§r §r§b(.*?)§r §r§.«§r"
saved_mapname = ""
mapname = ""
@tasks.loop(minutes=1)  # Check every minute
async def update_motd():
    global saved_mapname
    global timeonmap
    global mapname
    names = []
    print(timeonmap)
    """Check for the new MOTD and update the stored value."""
    currentstatus = await get_motd_from_server()
    new_motd = currentstatus.description
    print(currentstatus.players.sample)
    for player in currentstatus.players.sample:
        names.append(player.name)
    match = re.search(pattern, new_motd)
    print(new_motd)
    if match:
        if match.group(1) != "a":
            return
        mapname = match.group(2)
        if mapname != saved_mapname:
            save_mapname(mapname, names, currentstatus)
            print(f"map updated to: {mapname}")
            timeonmap = 0
        # if the motd hasn't changed in 1 minute
        else:
            print("map has not changed.")
            saved_mapname = mapname
            timeonmap += 1
            update_minutes(timeonmap)
        # output
        if CHANNEL_ID is not None:
            print(CHANNEL_ID)
            channel = bot.get_channel(CHANNEL_ID)  # Get the channel by ID
            if channel:
                if timeonmap == 60:
                    await channel.send(f"{mapname} has been going for 1 hour!")
                elif timeonmap == 120:
                    await channel.send(f"{mapname} has been going for 2 hours!")
                elif timeonmap == 180:
                    await channel.send(f"{mapname} has been going for 3 hours!")
                elif timeonmap == 240:
                    await channel.send(f"{mapname} has been going for 4 hours!")
                elif timeonmap == 300:
                    await channel.send(f"{mapname} has been going for 5 hours!")
                elif timeonmap == 360:
                    await channel.send(f"{mapname} has been going for 6 hours!")
                elif timeonmap == 420:
                    await channel.send(f"{mapname} has been going for 7 hours!")
                elif timeonmap == 480:
                    await channel.send(f"{mapname} has been going for 8 hours!")
                elif timeonmap == 540:
                    await channel.send(f"{mapname} has been going for 9 hours!")
                elif timeonmap == 600:
                    await channel.send(f"{mapname} has been going for 10 hours!")
            else:
                print("Could not find the channel!")
        else:
            print("channel not found")
    else:
        print("could not find map name")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # Start the task to update MOTD
    update_motd.start()

@bot.command()
async def channel(ctx, cid: str):
    global CHANNEL_ID
    """Command to fetch the current MOTD from central storage."""
    CHANNEL_ID = int(cid)
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await ctx.send(f"The current channel is set to: {channel}")
    else:
        await ctx.send("Could not find channel from ID.")
    print(f"current channel id: {CHANNEL_ID}")

# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))
