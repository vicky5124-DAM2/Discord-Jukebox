# Import the command handler
import hikari
import lightbulb

import os
from dotenv import load_dotenv

load_dotenv()

# Instantiate a Bot instance
bot = lightbulb.BotApp(
    token=os.environ["DISCORD_TOKEN"],
    prefix=os.environ["DISCORD_PREFIX"],
    default_enabled_guilds=list(filter(int, os.environ["DEFAULT_ENABLED_GUIDS"].split(','))),
    intents=hikari.Intents.ALL_MESSAGES
    | hikari.Intents.MESSAGE_CONTENT
    | hikari.Intents.GUILD_VOICE_STATES
    | hikari.Intents.GUILDS
    | hikari.Intents.GUILD_MEMBERS,
)

bot.load_extensions_from("./plugins")

# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
bot.run()
