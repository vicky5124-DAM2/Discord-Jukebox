import hikari

from lavalink_voice import LavalinkVoice

import random

import lightbulb
from hikari import GatewayBot
from lightbulb import Plugin, Context

plugin = Plugin("Music (advanced) commands")
plugin.add_checks(lightbulb.guild_only)


@plugin.command()
@lightbulb.command(
    "pause",
    "Pause the currently playing song",
    name_localizations={hikari.Locale.ES_ES: "pausa"},
    description_localizations={
        hikari.Locale.ES_ES: "Pausa la canción que se está reproduciendo " "actualmente"
    },
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def pause(ctx: Context) -> None:
    """Pause the currently playing song"""
    if not ctx.guild_id:
        return None
    # voice es la conexion al canal de voz
    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response"))
        return None
    # isinstance mira si voice es una instancia de LavalinkVoice
    assert isinstance(voice, LavalinkVoice)

    player = await voice.player_ctx.get_player()
    # este if mira si hay una canción reproduciendose ahora mismo
    if player.track:
        # este if mira si hay una uri
        if player.track.info.uri:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.pause.paused_url.response").format("player.track.info.author",
                                                                                          "player.track.info.title",
                                                                                          "player.track.info.uri")
            )
        else:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.pause.paused_no_url.response").format("player.track.info.author",
                                                                                             "player.track.info.title")
            )
        # este await pausa la cancion
        await voice.player_ctx.set_pause(True)
    else:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.pause.nothing_pause.response"))


@plugin.command()
@lightbulb.command(
    "resume",
    "Resume the currently playing song",
    name_localizations={hikari.Locale.ES_ES: "continuar"},
    description_localizations={
        hikari.Locale.ES_ES: "Continua la canción que se está reproduciendo actualmente"
    },
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def resume(ctx: Context) -> None:
    """Resume the currently playing song"""
    if not ctx.guild_id:
        return None
    # voice es la conexion al canal de voz
    voice = ctx.bot.voice.connections.get(ctx.guild_id)
    # si voice es nulo estonces el bot no está conectado a un canal de voz
    if not voice:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response"))
        return None
    # isinstance mira si voice es una instancia de LavalinkVoice
    assert isinstance(voice, LavalinkVoice)
    # player es el reproductor de musica que usa el bot cuando se une a un canal de voz
    player = await voice.player_ctx.get_player()
    # player.track es la canción que está en el reproductor (el if mira si hay una canción en el reproductor)
    if player.track:
        # este if mira si la canción tiene un url, si lo tiene saldrá en el mensaje del bot
        if player.track.info.uri:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.resume.resumed_url.response").format("player.track.info.author",
                                                                                            "player.track.info.title",
                                                                                            "player.track.info.uri")
            )
        else:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.resume.resumed_no_url.response").format(
                    "player.track.info.author", "player.track.info.title")
            )
        # el bot continua la canción
        await voice.player_ctx.set_pause(False)
    else:
        # el reproductor no tiene nignuna canción asi que no hay nada que continuar
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.resume.nothing_resume.response"))


@plugin.command()
@lightbulb.option(
    "seconds",
    "The position to jump to",
    int,
    name_localizations={hikari.Locale.ES_ES: "segundos"},
    description_localizations={
        hikari.Locale.ES_ES: "La posición a la que quieres saltar"
    },
)
@lightbulb.command(
    "seek",
    "Seek the currently playing song",
    name_localizations={hikari.Locale.ES_ES: "buscar"},
    description_localizations={
        hikari.Locale.ES_ES: "Salta la canción a un segundo en especifico"
    },
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def seek(ctx: Context) -> None:
    """Seek the currently playing song to a specific second"""
    if not ctx.guild_id:
        return None
    # voice es la conexion al canal de voz
    voice = ctx.bot.voice.connections.get(ctx.guild_id)
    # si voice es nulo estonces el bot no está conectado a un canal de voz
    if not voice:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response"))
        return None
    # isinstance mira si voice es una instancia de LavalinkVoice
    assert isinstance(voice, LavalinkVoice)
    # player es el reproductor de musica que usa el bot cuando se une a un canal de voz
    player = await voice.player_ctx.get_player()
    # player.track es la canción que está en el reproductor (el if mira si hay una canción en el reproductor)
    if player.track:
        # este if mira si la canción tiene un url, si lo tiene saldrá en el mensaje del bot
        if player.track.info.uri:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.seek.seeked_url.response").format("player.track.info.author",
                                                                                         "player.track.info.title",
                                                                                         "player.track.info.uri")
            )
        else:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.seek.seeked_no_url.response").format("player.track.info.author",
                                                                                            "player.track.info.title")
            )
        # el bot continua la canción en los segundos indicados multiplicados por 1000 (milisegundos)
        await voice.player_ctx.set_position_ms(ctx.options.seconds * 1000)
    else:
        # si no hay ninguna canción en el reproductor pone este mensaje
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.seek.nothing_seek.response"))


@plugin.command()
@lightbulb.command(
    "queue",
    "List the current queue",
    name_localizations={hikari.Locale.ES_ES: "cola"},
    description_localizations={hikari.Locale.ES_ES: "Lista la cola actual"},
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def queue(ctx: Context) -> None:
    """List the current queue"""
    if not ctx.guild_id:
        return None
    # voice es la conexion al canal de voz
    voice = ctx.bot.voice.connections.get(ctx.guild_id)
    # si voice es nulo estonces el bot no está conectado a un canal de voz
    if not voice:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response"))
        return None

    assert isinstance(voice, LavalinkVoice)

    player = await voice.player_ctx.get_player()

    now_playing = ctx.bot.d.localizer.get_text(ctx, "cmd.queue.now_playing.response")

    if player.track:
        # este es el tiempo de la canción en segundos (dentro del minuto)
        time_s = int(player.state.position / 1000 % 60)
        # este es el tiempo de la canción en minutos
        time_m = int(player.state.position / 1000 / 60 % 60)
        # este es el tiempo de la canción en horas (por si la canción dura más de una hora)
        time_h = int(player.state.position / 1000 / 60 / 60)
        # este es el tiempo total de la canción en segundos, necessario para `/seek <t>`
        time_true_s = int(player.state.position / 1000)
        # el tiempo de la canción (time_h son las horas, time_m son los minutos, y time_s son los segundos)
        if time_h:
            time = f"{time_h:02}:{time_m:02}:{time_s:02}"
        else:
            time = f"{time_m:02}:{time_s:02}"

        if player.track.info.uri:
            ctx.bot.d.localizer.get_text(ctx, "cmd.queue.now_playing_url.response").format("player.track.info.author",
                                                                                           "player.track.info.title",
                                                                                           "player.track.info.uri",
                                                                                           "time",
                                                                                           "time_true_s")
        else:
            ctx.bot.d.localizer.get_text(ctx, "cmd.queue.now_playing_no_url.response").format(
                "player.track.info.author", "player.track.info.title", "time", "time_true_s")
    # queue es la lista de canciones que hay en la cola
    queue = await voice.player_ctx.get_queue()
    queue_text = ""
    # enumerate enumera el numero de canciones en la cola y su información, el máximo de canciones en la cola es 10
    for idx, i in enumerate(queue):
        if idx == 9:
            break

        if i.track.info.uri:
            queue_text += f"{idx + 1} -> [`{i.track.info.author} - {i.track.info.title}`](<{i.track.info.uri}>)\n"
        else:
            queue_text += (
                f"{idx + 1} -> `{i.track.info.author} - {i.track.info.title}`\n"
            )

    if not queue_text:
        queue_text = ctx.bot.d.localizer.get_text(ctx, "cmd.queue.queue_text.response")

    await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.queue.now_playing_queue.response").format(
        "now_playing", "queue_text"))


@plugin.command()
@lightbulb.option(
    "index",
    "The index of the song to remove",
    int,
    name_localizations={hikari.Locale.ES_ES: "indice"},
    description_localizations={
        hikari.Locale.ES_ES: "El indice de la canción a eliminar"
    },
)
@lightbulb.command(
    "remove",
    "Remove the song at the specified index from the queue",
    name_localizations={hikari.Locale.ES_ES: "quitar"},
    description_localizations={
        hikari.Locale.ES_ES: "Quita la canción del indice especificado de la cola"
    },
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def remove(ctx: Context) -> None:
    """Remove the song at the specified index from the queue"""
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response"))
        return None

    assert isinstance(voice, LavalinkVoice)

    queue = await voice.player_ctx.get_queue()
    # si el indice indicado por el usuario es mayor a la longitud de la cola, saldrá este mensaje
    if ctx.options.index > len(queue):
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.remove.index_out_range.response"))
        return None

    assert isinstance(ctx.options.index, int)
    track = queue[ctx.options.index - 1].track

    if track.info.uri:
        await ctx.respond(
            ctx.bot.d.localizer.get_text(ctx, "cmd.remove.removed_url.response").format(
                "track.info.author", "track.info.title", "track.info.uri")
        )
    else:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.remove.removed_url.response").format(
                "track.info.author", "track.info.title"))
    # el indice de la cola se reduce en uno
    voice.player_ctx.set_queue_remove(ctx.options.index - 1)


@plugin.command()
@lightbulb.command(
    "clear",
    "Clear the entire queue",
    name_localizations={hikari.Locale.ES_ES: "limpiar"},
    description_localizations={hikari.Locale.ES_ES: "Limpia toda la cola"},
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def clear(ctx: Context) -> None:
    """Clear the entire queue"""
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response"))
        return None

    assert isinstance(voice, LavalinkVoice)

    queue = await voice.player_ctx.get_queue()

    if not queue:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.clear.queue_empty.response"))
        return None
    # da la cola vacia a voice
    voice.player_ctx.set_queue_clear()
    await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.clear.queue_cleared.response"))


@plugin.command()
@lightbulb.option(
    "index1",
    "The index of the one of the songs to swap",
    int,
    name_localizations={hikari.Locale.ES_ES: "indice1"},
    description_localizations={
        hikari.Locale.ES_ES: "El indice de una de las canciones a intercambiar"
    },
)
@lightbulb.option(
    "index2",
    "The index of the other song to swap",
    int,
    name_localizations={hikari.Locale.ES_ES: "indice2"},
    description_localizations={
        hikari.Locale.ES_ES: "El indice de la otra canción a intercambiar"
    },
)
@lightbulb.command(
    "swap",
    "Swap the places of two songs in the queue",
    name_localizations={hikari.Locale.ES_ES: "intercambiar"},
    description_localizations={
        hikari.Locale.ES_ES: "Intercambia entre si los lugares de dos canciones en la cola"
    },
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def swap(ctx: Context) -> None:
    """Swap the places of two songs in the queue"""
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response"))
        return None

    assert isinstance(voice, LavalinkVoice)

    queue = await voice.player_ctx.get_queue()
    # mira si el indice indicado por el usuario es mayor a la longitud de la cola
    if ctx.options.index1 > len(queue):
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.swap.index1_out_range.response"))
        return None
    # mira si el indice indicado por el usuario es mayor a la longitud de la cola
    if ctx.options.index2 > len(queue):
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.swap.index2_out_range.response"))
        return None
    # mira si los dos indices son el mismo
    if ctx.options.index1 == ctx.options.index2:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.swap.same_indexes.response"))
        return None

    assert isinstance(ctx.options.index1, int)
    assert isinstance(ctx.options.index2, int)

    track1 = queue[ctx.options.index1 - 1]
    track2 = queue[ctx.options.index2 - 1]
    # se intercambian los indices de las dos canciones
    queue[ctx.options.index1 - 1] = track2
    queue[ctx.options.index2 - 1] = track1
    # da la cola modificada a voice
    voice.player_ctx.set_queue_replace(queue)

    if track1.track.info.uri:
        track1_text = f"[`{track1.track.info.author} - {track1.track.info.title}`](<{track1.track.info.uri}>)"
    else:
        track1_text = f"`{track1.track.info.author} - {track1.track.info.title}`"

    if track2.track.info.uri:
        track2_text = f"[`{track2.track.info.author} - {track2.track.info.title}`](<{track2.track.info.uri}>)"
    else:
        track2_text = f"`{track2.track.info.author} - {track2.track.info.title}`"

    await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.swap.swapped.response").format("track2_text",
                                                                                            "track1_text"))


@plugin.command()
@lightbulb.command(
    "shuffle",
    "Shuffle the queue",
    name_localizations={hikari.Locale.ES_ES: "mezclar"},
    description_localizations={hikari.Locale.ES_ES: "Mezcla la cola"},
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def shuffle(ctx: Context) -> None:
    """Shuffle the queue"""
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response"))
        return None

    assert isinstance(voice, LavalinkVoice)

    queue = await voice.player_ctx.get_queue()
    # se mezclan los indices de la cola
    random.shuffle(queue)
    # da la cola modificada a voice
    voice.player_ctx.set_queue_replace(queue)

    await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.shuffle.queue_shuffled.response"))


@plugin.command()
@lightbulb.command(
    "loop",
    "Loops the current song when it ends",
    name_localizations={hikari.Locale.ES_ES: "bucle"},
    description_localizations={
        hikari.Locale.ES_ES: "Vuelve a reproducir la misma canción cuando esta termina"
    },
)
@lightbulb.implements(lightbulb.PrefixCommandGroup, lightbulb.SlashCommandGroup)
async def loop(ctx: Context) -> None:
    return None


# @loop.child hace que /loop start sea un subcomando de loop
@loop.child
@lightbulb.command(
    "start",
    "Starts the loop",
    auto_defer=True,
    name_localizations={hikari.Locale.ES_ES: "iniciar"},
    description_localizations={hikari.Locale.ES_ES: "Inicia el bucle"},
)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def loop_start(ctx: Context) -> None:
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response"))
        return None

    assert isinstance(voice, LavalinkVoice)

    player = await voice.player_ctx.get_player()

    if player.track:
        voice.player_ctx.set_queue_push_to_front(player.track)
        if voice.lavalink.data:
            voice.lavalink.data.append(ctx.guild_id)
        else:
            voice.lavalink.data = [ctx.guild_id]

        if player.track.info.uri:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.loop_start.starting_loop_url.response").format(
                    "player.track.info.author", "player.track.info.title", "player.track.info.uri")
            )
        else:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.loop_start.starting_loop_no_url.response").format(
                    "player.track.info.author", "player.track.info.title")
            )
    else:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.loop.nothing_playing.response"))


# @loop.child hace que /loop end sea un subcomando de loop
@loop.child
@lightbulb.command(
    "end",
    "Ends the loop",
    auto_defer=True,
    name_localizations={hikari.Locale.ES_ES: "finalizar"},
    description_localizations={hikari.Locale.ES_ES: "Finaliza el bucle"},
)
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def loop_end(ctx: Context) -> None:
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response"))
        return None

    assert isinstance(voice, LavalinkVoice)

    player = await voice.player_ctx.get_player()

    if player.track:
        voice.player_ctx.set_queue_remove(0)
        if voice.lavalink.data:
            voice.lavalink.data.remove(ctx.guild_id)
        if player.track.info.uri:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.loop_end.ending_loop_url.response").format(
                    "player.track.info.author", "player.track.info.title", "player.track.info.uri")
            )
        else:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.loop_end.ending_loop_no_url.response").format(
                    "player.track.info.author", "player.track.info.title")
            )
    else:
        await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.loop.nothing_playing.response"))


def load(bot: GatewayBot) -> None:
    bot.add_plugin(plugin)
