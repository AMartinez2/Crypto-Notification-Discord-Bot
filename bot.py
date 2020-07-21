import discord
from discord.ext import commands
import asyncio
from asyncio import sleep
import json
import ledgerControl


CONFIG = json.load(open('.config'))

client  = commands.Bot(command_prefix = '.')


async def ledgerLoop():
    await client.wait_until_ready()
    channel = client.get_channel(CONFIG['discordChannelId'])
    while not client.is_closed():
        processNotifs = ledgerControl.ledgerProcess()
        for i in processNotifs:
            await channel.send(i)
        await asyncio.sleep(5)


@client.event
async def on_ready():
    channel = client.get_channel(CONFIG['discordChannelId'])
    await channel.send('bot startup')
    if (not ledgerControl.ledgerFileExists()):
        ledgerControl.initLedger()
    await channel.send('Verifying ledger...')
    if (not ledgerControl.verifyLedger()):
        await channel.send('Ledger verification failed, initializing new ledger...')
        ledgerControl.initLedger()
    else:
        await channel.send('Ledger verification complete.')


async def on_message():
    channel = client.get_channel(CONFIG['discordChannelId'])
    await channel.send('@everyone hello')


client.loop.create_task(ledgerLoop())
client.run(CONFIG['discordToken'])
