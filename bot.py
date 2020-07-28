import discord
from discord.ext import commands
import asyncio
from asyncio import sleep
import json
import ledgerControl


CONFIG = json.load(open('.config'))

Client  = commands.Bot(command_prefix = '!')


async def ledgerLoop():
    await Client.wait_until_ready()
    channel = Client.get_channel(CONFIG['discordChannelId'])
    while not Client.is_closed():
        processNotifs = ledgerControl.ledgerProcess()
        for i in processNotifs:
            await channel.send(i)
        await asyncio.sleep(5)


@Client.event
async def on_ready():
    channel = Client.get_channel(CONFIG['discordChannelId'])
    await channel.send('bot startup')
    if (not ledgerControl.ledgerFileExists()):
        ledgerControl.initLedger()
    await channel.send('Verifying ledger...')
    if (not ledgerControl.verifyLedger()):
        await channel.send('Ledger verification failed, initializing new ledger...')
        ledgerControl.initLedger()
    else:
        await channel.send('Ledger verification complete.')


@Client.event
async def on_message(message):
    channel = Client.get_channel(CONFIG['discordChannelId'])
    if (message.content[0] == '!'):
        await message.channel.send('accepting commands')
    if (message.content.startswith('!waffles')):
        await message.channel.send('waffles you bitch')


Client.loop.create_task(ledgerLoop())
Client.run(CONFIG['discordToken'])
