import lightbulb

plugin = lightbulb.Plugin("Meta Plugin")


# Register the command to the bot
@plugin.command
# Use the command decorator to convert the function into a command
@lightbulb.command("ping", "checks the bot is alive")
# Define the command type(s) that this command implements
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
# Define the command's callback. The callback should take a single argument which will be
# an instance of a subclass of lightbulb.context.Context when passed in
async def ping(ctx: lightbulb.Context) -> None:
    # Send a message to the channel the command was used in
    await ctx.respond("Pong!")


@plugin.command()
@lightbulb.option("text", "Text to repeat", modifier=lightbulb.OptionModifier.CONSUME_REST)
@lightbulb.command("echo", "Repeats the user's input")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def echo(ctx: lightbulb.Context) -> None:
    await ctx.respond(ctx.options.text)

@plugin.command()
@lightbulb.option("addend2", "Second addend", float)
@lightbulb.option("addend1", "First addend", float)
@lightbulb.command("add", "Add two numbers")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def add(ctx: lightbulb.Context) -> None:
    await ctx.respond(ctx.options.addend1 + ctx.options.addend2)

@plugin.command()
@lightbulb.option("substract2", "Second substract", float)
@lightbulb.option("substract1", "First substract", float)
@lightbulb.command("substract", "Substract two numbers")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def substract(ctx: lightbulb.Context) -> None:
    await ctx.respond(ctx.options.substract1 - ctx.options.substract2)

@plugin.command()
@lightbulb.option("factor2", "Second factor", float)
@lightbulb.option("factor1", "First factor", float)
@lightbulb.command("multiplication", "Multiplies two numbers")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def multiplication(ctx: lightbulb.Context) -> None:
    await ctx.respond(ctx.options.factor1 * ctx.options.factor2)

@plugin.command()
@lightbulb.option("divisor", "Divisor", float)
@lightbulb.option("dividend", "Dividend", float)
@lightbulb.command("division", "Divides the two numbers")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def division(ctx: lightbulb.Context) -> None:
    await ctx.respond(ctx.options.dividend / ctx.options.divisor)


def load(bot):
    bot.add_plugin(plugin)
