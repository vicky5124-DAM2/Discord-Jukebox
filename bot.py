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
    default_enabled_guilds=1214648265836990524,
    intents=hikari.Intents.ALL_MESSAGES
    | hikari.Intents.GUILDS
    | hikari.Intents.MESSAGE_CONTENT
    | hikari.Intents.GUILD_VOICE_STATES
    | hikari.Intents.GUILD_MEMBERS,
)


# Register the command to the bot
@bot.command
# Use the command decorator to convert the function into a command
@lightbulb.command("ping", "checks the bot is alive")
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def ping(ctx: lightbulb.Context) -> None:
    # Send a message to the channel the command was used in
    await ctx.respond("Pong!")

# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
bot.run()
