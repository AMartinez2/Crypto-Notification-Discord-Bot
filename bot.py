import discord
from discord.ext import commands
from asyncio import sleep

CONFIG = json.load(open('.config'))

client  = commands.Bot(command_prefix = '.')

# @loop(seconds=10)
# async def name_change():
#     print('waffles')
#     # await client.change_presence(...)
#     await sleep(10)
#     # await client.change_presence(...)

# async def my_background_task():
#     await client.wait_until_ready()
#     counter = 0
#     channel = discord.Object(id='channel_id_here')
#     while not client.is_closed:
#         counter += 1
#         await client.send_message(channel, counter)
#         await asyncio.sleep(5) # task runs every 60 seconds


@client.event
async def on_ready():
    channel = client.get_channel(CONFIG['discordChannelId'])
    await channel.send('@everyone hello')
    print('wowo')
    # print(os.system('python main.py'))
    print('yowza')


async def on_message():
    print('what')
    channel = client.get_channel(CONFIG['discordChannelId'])
    await channel.send('@everyone hello')


client.run(CONFIG['discordToken'])
