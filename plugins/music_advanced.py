from lavalink_voice import LavalinkVoice

import random

import lightbulb
from hikari import GatewayBot
from lightbulb import Plugin, Context

plugin = Plugin("Music (advanced) commands")
plugin.add_checks(lightbulb.guild_only)


@plugin.command()
@lightbulb.command("pause", "Pause the currently playing song")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def pause(ctx: Context) -> None:
    """Pause the currently playing song"""
    if not ctx.guild_id:
        return None
    # voice es la conexion al canal de voz
    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond("Not connected to a voice channel")
        return None
    # isinstance mira si voice es una instancia de LavalinkVoice
    assert isinstance(voice, LavalinkVoice)

    player = await voice.player.get_player()
    # este if mira si hay una canción reproduciendose ahora mismo
    if player.track:
        # este if mira si hay una uri
        if player.track.info.uri:
            await ctx.respond(
                f"Paused: [`{player.track.info.author} - {player.track.info.title}`](<{player.track.info.uri}>)"
            )
        else:
            await ctx.respond(
                f"Paused: `{player.track.info.author} - {player.track.info.title}`"
            )
        # este await pausa la cancion
        await voice.player.set_pause(True)
    else:
        await ctx.respond("Nothing to pause")


@plugin.command()
@lightbulb.command("resume", "Resume the currently playing song")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def resume(ctx: Context) -> None:
    """Resume the currently playing song"""
    if not ctx.guild_id:
        return None
    # voice es la conexion al canal de voz
    voice = ctx.bot.voice.connections.get(ctx.guild_id)
    # si voice es nulo estonces el bot no está conectado a un canal de voz
    if not voice:
        await ctx.respond("Not connected to a voice channel")
        return None
    # isinstance mira si voice es una instancia de LavalinkVoice
    assert isinstance(voice, LavalinkVoice)
    # player es el reproductor de musica que usa el bot cuando se une a un canal de voz
    player = await voice.player.get_player()
    # player.track es la canción que está en el reproductor (el if mira si hay una canción en el reproductor)
    if player.track:
        # este if mira si la canción tiene un url, si lo tiene saldrá en el mensaje del bot
        if player.track.info.uri:
            await ctx.respond(
                f"Resumed: [`{player.track.info.author} - {player.track.info.title}`](<{player.track.info.uri}>)"
            )
        else:
            await ctx.respond(
                f"Resumed: `{player.track.info.author} - {player.track.info.title}`"
            )
        # el bot continua la canción
        await voice.player.set_pause(False)
    else:
        # el reproductor no tiene nignuna canción asi que no hay nada que continuar
        await ctx.respond("Nothing to resume")


@plugin.command()
@lightbulb.option(
    "seconds",
    "The position to jump to",
    int,
)
@lightbulb.command("seek", "Seek the currently playing song")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def seek(ctx: Context) -> None:
    """Seek the currently playing song to a specific second"""
    if not ctx.guild_id:
        return None
    # voice es la conexion al canal de voz
    voice = ctx.bot.voice.connections.get(ctx.guild_id)
    # si voice es nulo estonces el bot no está conectado a un canal de voz
    if not voice:
        await ctx.respond("Not connected to a voice channel")
        return None
    # isinstance mira si voice es una instancia de LavalinkVoice
    assert isinstance(voice, LavalinkVoice)
    # player es el reproductor de musica que usa el bot cuando se une a un canal de voz
    player = await voice.player.get_player()
    # player.track es la canción que está en el reproductor (el if mira si hay una canción en el reproductor)
    if player.track:
        # este if mira si la canción tiene un url, si lo tiene saldrá en el mensaje del bot
        if player.track.info.uri:
            await ctx.respond(
                f"Seeked: [`{player.track.info.author} - {player.track.info.title}`](<{player.track.info.uri}>)"
            )
        else:
            await ctx.respond(
                f"Seeked: `{player.track.info.author} - {player.track.info.title}`"
            )
        # el bot continua la canción en los segundos indicados multiplicados por 1000 (milisegundos)
        await voice.player.set_position_ms(ctx.options.seconds * 1000)
    else:
        # si no hay ninguna canción en el reproductor pone este mensaje
        await ctx.respond("Nothing to seek")


@plugin.command()
@lightbulb.command("queue", "List the current queue")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def queue(ctx: Context) -> None:
    """List the current queue"""
    if not ctx.guild_id:
        return None
    # voice es la conexion al canal de voz
    voice = ctx.bot.voice.connections.get(ctx.guild_id)
    # si voice es nulo estonces el bot no está conectado a un canal de voz
    if not voice:
        await ctx.respond("Not connected to a voice channel")
        return None

    assert isinstance(voice, LavalinkVoice)

    player = await voice.player.get_player()

    now_playing = "Nothing"

    if player.track:
        # este es el tiempo de la canción en segundos (dentro del minuto)
        time_s = int(player.state.position / 1000 % 60)
        # este es el tiempo de la canción en minutos
        time_m = int(player.state.position / 1000 / 60 % 60)
        # este es el tiempo de la canción en horas (por si la canción dura más de una hora)
        time_h = int(player.state.position / 1000 / 60 / 60)
        #este es el tiempo total de la canción en segundos, necessario para `/seek <t>`
        time_true_s = int(player.state.position / 1000)
        # el tiempo de la canción (time_h son las horas, time_m son los minutos, y time_s son los segundos)
        if time_h:
            time = f"{time_h:02}:{time_m:02}:{time_s:02}"
        else:
            time = f"{time_m:02}:{time_s:02}"

        if player.track.info.uri:
            now_playing = f"[`{player.track.info.author} - {player.track.info.title}`](<{player.track.info.uri}>) | {time} (Second {time_true_s})"
        else:
            now_playing = f"`{player.track.info.author} - {player.track.info.title}` | {time} (Second {time_true_s})"
    # queue es la lista de canciones que hay en la cola
    queue = await voice.player.get_queue()
    queue_text = ""
    # enumerate enumera el numero de canciones en la cola y su información, el máximo de canciones en la cola es 10
    for idx, i in enumerate(queue):
        if idx == 9:
            break

        if i.track.info.uri:
            queue_text += f"{idx + 1} -> [`{i.track.info.author} - {i.track.info.title}`](<{i.track.info.uri}>)\n"
        else:
            queue_text += f"{idx + 1} -> `{i.track.info.author} - {i.track.info.title}`\n"

    if not queue_text:
        queue_text = "Empty queue"

    await ctx.respond(f"Now playing: {now_playing}\n\n{queue_text}")


@plugin.command()
@lightbulb.option(
    "index",
    "The index of the song to remove",
    int,
)
@lightbulb.command("remove", "Remove the song at the specified index from the queue")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def remove(ctx: Context) -> None:
    """Remove the song at the specified index from the queue"""
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond("Not connected to a voice channel")
        return None

    assert isinstance(voice, LavalinkVoice)

    queue = await voice.player.get_queue()
    # si el indice indicado por el usuario es mayor a la longitud de la cola, saldrá este mensaje
    if ctx.options.index > len(queue):
        await ctx.respond("Index out of range")
        return None

    assert isinstance(ctx.options.index, int)
    track = queue[ctx.options.index - 1].track

    if track.info.uri:
        await ctx.respond(
            f"Removed: [`{track.info.author} - {track.info.title}`](<{track.info.uri}>)"
        )
    else:
        await ctx.respond(f"Removed: `{track.info.author} - {track.info.title}`")
    # el indice de la cola se reduce en uno
    voice.player.set_queue_remove(ctx.options.index - 1)


@plugin.command()
@lightbulb.command("clear", "Clear the entire queue")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def clear(ctx: Context) -> None:
    """Clear the entire queue"""
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond("Not connected to a voice channel")
        return None

    assert isinstance(voice, LavalinkVoice)

    queue = await voice.player.get_queue()

    if not queue:
        await ctx.respond("The queue is already empty")
        return None
    # da la cola vacia a voice
    voice.player.set_queue_clear()
    await ctx.respond("The queue has been cleared")


@plugin.command()
@lightbulb.option(
    "index1",
    "The index of the one of the songs to swap",
    int,
)
@lightbulb.option(
    "index2",
    "The index of the other song to swap",
    int,
)
@lightbulb.command("swap", "Swap the places of two songs in the queue")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def swap(ctx: Context) -> None:
    """Swap the places of two songs in the queue"""
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond("Not connected to a voice channel")
        return None

    assert isinstance(voice, LavalinkVoice)

    queue = await voice.player.get_queue()
    # mira si el indice indicado por el usuario es mayor a la longitud de la cola
    if ctx.options.index1 > len(queue):
        await ctx.respond("Index 1 out of range")
        return None
    # mira si el indice indicado por el usuario es mayor a la longitud de la cola
    if ctx.options.index2 > len(queue):
        await ctx.respond("Index 2 out of range")
        return None
    # mira si los dos indices son el mismo
    if ctx.options.index1 == ctx.options.index2:
        await ctx.respond("Can't swap between the same indexes")
        return None

    assert isinstance(ctx.options.index1, int)
    assert isinstance(ctx.options.index2, int)

    track1 = queue[ctx.options.index1 - 1]
    track2 = queue[ctx.options.index2 - 1]
    # se intercambian los indices de las dos canciones
    queue[ctx.options.index1 - 1] = track2
    queue[ctx.options.index2 - 1] = track1
    # da la cola modificada a voice
    voice.player.set_queue_replace(queue)

    if track1.track.info.uri:
        track1_text = f"[`{track1.track.info.author} - {track1.track.info.title}`](<{track1.track.info.uri}>)"
    else:
        track1_text = f"`{track1.track.info.author} - {track1.track.info.title}`"

    if track2.track.info.uri:
        track2_text = f"[`{track2.track.info.author} - {track2.track.info.title}`](<{track2.track.info.uri}>)"
    else:
        track2_text = f"`{track2.track.info.author} - {track2.track.info.title}`"

    await ctx.respond(f"Swapped {track2_text} with {track1_text}")


@plugin.command()
@lightbulb.command("shuffle", "Shuffle the queue")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def shuffle(ctx: Context) -> None:
    """Shuffle the queue"""
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond("Not connected to a voice channel")
        return None

    assert isinstance(voice, LavalinkVoice)

    queue = await voice.player.get_queue()
    # se mezclan los indices de la cola
    random.shuffle(queue)
    # da la cola modificada a voice
    voice.player.set_queue_replace(queue)

    await ctx.respond("Shuffled the queue")

@plugin.command()
@lightbulb.option(
    "start",
    "Starts the loop"
)
@lightbulb.option(
    "end",
    "Ends the loop"
)
@lightbulb.command("loop", "Loops the current song when it ends")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def loop(ctx:Context) -> None:
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond("Not connected to a voice channel")
        return None

    assert isinstance(voice, LavalinkVoice)

    player = await voice.player.get_player()

    if player.track:
        if player.state.position == player.track.info.length:
            


def load(bot: GatewayBot) -> None:
    bot.add_plugin(plugin)
