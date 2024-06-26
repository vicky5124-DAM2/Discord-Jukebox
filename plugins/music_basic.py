import asyncio
import sys
import traceback
from pprint import pprint

from lavalink_rs import PlayerContext
from lavalink_rs.model.search import SearchEngines

from lavalink_voice import LavalinkVoice

import logging
import typing as t

import hikari
import yt_dlp
import lightbulb
from hikari import GatewayBot
from lightbulb import Plugin, Context
from lavalink_rs.model.track import TrackData, PlaylistData, TrackLoadType

plugin = Plugin("Music (basic) commands")
plugin.add_checks(lightbulb.guild_only)

ytdl_format_options = {
    "format": "bestaudio/best",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


async def _join(ctx: Context) -> t.Optional[hikari.Snowflake]:
    if not ctx.guild_id:
        return None
    # channel_id es el id del canal de voz donde se conectará el bot
    channel_id = None
    # ctx.options.items son los parametros del comando. El for recorre las distintas opciones.
    for i in ctx.options.items():
        # si channel es el nombre del parametro y tiene un valor presente en el comando...
        if i[0] == "channel" and i[1]:
            # ... entonces el bot entra en el canal especificado (i[1].id)
            channel_id = i[1].id
            break
    # si no tiene ningún canal especificado en el comando (es solo !join o /join)...
    if not channel_id:
        # ...entra en el canal en el que está el usuario que ha escrito el comando
        voice_state = ctx.bot.cache.get_voice_state(ctx.guild_id, ctx.author.id)
        # si el usuario no está conectado a ningún canal
        if not voice_state or not voice_state.channel_id:
            return None
        # channel_id es el canal al que está conectado el usuario
        channel_id = voice_state.channel_id
    # miramos si el bot ya está conectado a ese canal
    voice = ctx.bot.voice.connections.get(ctx.guild_id)
    # si no está conectado a ningún canal, entonces se conecta al canal introducido en el comando,
    # o en el que está el usuario
    if not voice:
        locale = None
        if ctx.interaction:
            locale = ctx.interaction.locale
        voice = await LavalinkVoice.connect(
            ctx.guild_id,
            channel_id,
            ctx.bot,
            ctx.bot.d.lavalink,
            (ctx.channel_id, ctx.bot, locale),
        )

    return channel_id


@plugin.command()
@lightbulb.option(
    "channel",
    "The channel you want me to join",
    hikari.GuildVoiceChannel,
    required=False,
    channel_types=[hikari.ChannelType.GUILD_VOICE],
    name_localizations={hikari.Locale.ES_ES: "canal"},
    description_localizations={
        hikari.Locale.ES_ES: "El canal al que quieres que me una"
    },
)
@lightbulb.command(
    "join",
    "Enters the voice channel you are connected to, or the one specified",
    auto_defer=True,
    name_localizations={hikari.Locale.ES_ES: "unir"},
    description_localizations={
        hikari.Locale.ES_ES: "Entra el canal de voz al que estás conectado, "
        "o al especificado en el comando"
    },
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def join(ctx: Context) -> None:
    """Joins the voice channel you are in"""
    channel_id = await _join(ctx)

    if channel_id:
        await ctx.respond(
            ctx.bot.d.localizer.get_text(ctx, "cmd.join.channel_id.response").format(
                channel_id
            )
        )
    else:
        await ctx.respond(
            ctx.bot.d.localizer.get_text(ctx, "cmd.join.please_join_channel.response")
        )


@plugin.command()
@lightbulb.command(
    "leave",
    "Leaves the voice channel",
    auto_defer=True,
    name_localizations={hikari.Locale.ES_ES: "salir"},
    description_localizations={hikari.Locale.ES_ES: "El bot sale del canal de voz"},
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def leave(ctx: Context) -> None:
    """Leaves the voice channel"""
    if not ctx.guild_id:
        return None
    # miramos si el bot está conectado en un canal
    voice = ctx.bot.voice.connections.get(ctx.guild_id)
    # si no está en ningún canal, el bot introducirá un mensaje diciendolo
    if not voice:
        await ctx.respond(
            ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response")
        )
        return None
    # el bot se desconecta del canal
    await voice.disconnect()

    await ctx.respond(
        ctx.bot.d.localizer.get_text(ctx, "cmd.leave.left_channel.response")
    )


@plugin.command()
@lightbulb.option(
    "query",
    "The spotify search query, or any URL",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
    required=False,
    name_localizations={hikari.Locale.ES_ES: "busqueda"},
    description_localizations={
        hikari.Locale.ES_ES: "La busqueda en spotify, o cualquier URL"
    },
)
@lightbulb.command(
    "play",
    "Searches the query on spotify and adds the first result to the queue, or adds the URL to the queue",
    auto_defer=True,
    name_localizations={hikari.Locale.ES_ES: "reproducir"},
    description_localizations={
        hikari.Locale.ES_ES: "Busca la consulta en Spotify y agrega el primer resultado a la "
        "cola, o agrega la URL a la cola"
    },
)
@lightbulb.implements(
    lightbulb.PrefixCommand,
    lightbulb.SlashCommand,
)
async def play(ctx: Context) -> None:
    if not ctx.guild_id:
        return None

    voice = ctx.bot.voice.connections.get(ctx.guild_id)
    has_joined = False

    if not voice:
        if not await _join(ctx):
            await ctx.respond(
                ctx.bot.d.localizer.get_text(
                    ctx, "cmd.play.join_please_join_channel.response"
                )
            )
            return None
        voice = ctx.bot.voice.connections.get(ctx.guild_id)
        has_joined = True

    assert isinstance(voice, LavalinkVoice)

    player_ctx = voice.player_ctx

    # si no hay argumentos en el comando, sigue la reproducción a partir de la siguiente canción
    # después de haber usado un /stop
    if not ctx.options.query:
        player = await player_ctx.get_player()
        # si no hay ninguna canción reproduciendose y hay canciones en la cola...
        if not player.track and await player_ctx.get_queue().get_count():
            # el bot hará un /skip para reproducir la siguiente canción
            player_ctx.skip()
        # si ya hay una canción, entonces el bot pondrá un mensaje
        elif player.track:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(
                    ctx, "cmd.play.song_already_playing.response"
                )
            )
        # y si no hay ninguna canción en la cola, el bot pondrá otro mensaje
        else:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.play.empty_queue.response")
            )

        return None

    # hacemos replace de < y > por un "" para evitar que los enlaces sean invalidos
    query = ctx.options.query.replace(">", "").replace("<", "")

    # si no es una url, el bot buscará el argumento indicado por el usuario en youtube
    if not query.startswith("http"):
        query = SearchEngines.spotify(query)

    try:
        # loaded_tracks son los resultados de la busqueda del bot o del url
        tracks = await ctx.bot.d.lavalink.load_tracks(ctx.guild_id, query)
        loaded_tracks = tracks.data
    # si loaded_tracks está vacío, entonces la excepción buscará la query en yt_dlp
    except Exception as e:
        try:
            await play_yt_dlp(query, ctx, player_ctx, has_joined)
        # si la aplicación no soporta la url entonces saldrá una excepción con un mensaje anunciandolo
        # except yt_dlp.UnsupportedUrl:
        #    await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "cmd.play.url_not_supported"))
        except Exception as e:
            # logging.error son mensajes que salen cuando corres la aplicación
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
            logging.error(e)
            await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "error.response"))
        return None

    # Single track
    # este if mira si el resultado de la query hay resultados, si es una canción, una playlist, si está vacío o si
    # hay un error
    if tracks.load_type == TrackLoadType.Track:
        loaded_tracks.user_data = {"requester_id": int(ctx.author.id)}
        player_ctx.queue(loaded_tracks)
        # si hay url, la pone en el mensaje de la información de la canción cuando empieza la canción
        if loaded_tracks.info.uri:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(
                    ctx, "cmd.play.added_to_queue.response"
                ).format(
                    ctx.bot.d.localizer.get_text(ctx, "generic.track_info_url").format(
                        loaded_tracks.info.author,
                        loaded_tracks.info.title,
                        loaded_tracks.info.uri,
                        loaded_tracks.user_data["requester_id"],
                    )
                )
            )
        # si no, pone el mensaje sin la url
        else:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(
                    ctx, "cmd.play.added_to_queue.response"
                ).format(
                    ctx.bot.d.localizer.get_text(
                        ctx, "generic.track_info_no_url"
                    ).format(
                        loaded_tracks.info.author,
                        loaded_tracks.info.title,
                        loaded_tracks.user_data["requester_id"],
                    )
                )
            )

    # Search results
    # este elif coge el primer resultado de la busqueda de la query (cuando no se pone un enlace de música)
    elif tracks.load_type == TrackLoadType.Search:
        loaded_tracks[0].user_data = {"requester_id": int(ctx.author.id)}
        player_ctx.queue(loaded_tracks[0])
        # si hay url, la pone en el mensaje de la información de la canción cuando empieza la canción
        if loaded_tracks[0].info.uri:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(
                    ctx, "cmd.play.added_to_queue.response"
                ).format(
                    ctx.bot.d.localizer.get_text(ctx, "generic.track_info_url").format(
                        loaded_tracks[0].info.author,
                        loaded_tracks[0].info.title,
                        loaded_tracks[0].info.uri,
                        loaded_tracks[0].user_data["requester_id"],
                    )
                )
            )
        # si no, pone el mensaje sin la url
        else:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(
                    ctx, "cmd.play.added_to_queue.response"
                ).format(
                    ctx.bot.d.localizer.get_text(
                        ctx, "generic.track_info_no_url"
                    ).format(
                        loaded_tracks[0].info.author,
                        loaded_tracks[0].info.title,
                        loaded_tracks[0].user_data["requester_id"],
                    )
                )
            )

    # Playlist
    # se llega a este elif cuando pones una playlist en la query
    elif tracks.load_type == TrackLoadType.Playlist:
        # en este if se pone la información del video del enlace (que está dentro de una playlist)
        if loaded_tracks.info.selected_track:
            # se añade la playlist a la cola con el video del enlace en primer lugar
            track = loaded_tracks.tracks[loaded_tracks.info.selected_track]
            track.user_data = {"requester_id": int(ctx.author.id)}
            player_ctx.queue(track)
            # si hay url, la pone en el mensaje de la información de la canción cuando empieza la canción
            if track.info.uri:
                await ctx.respond(
                    ctx.bot.d.localizer.get_text(
                        ctx, "cmd.play.added_to_queue.response"
                    ).format(
                        ctx.bot.d.localizer.get_text(
                            ctx, "generic.track_info_url"
                        ).format(
                            track.info.author,
                            track.info.title,
                            track.info.uri,
                            track.user_data["requester_id"],
                        )
                    )
                )
            # si no hay url, entonces se pone la información sin la url
            else:
                await ctx.respond(
                    ctx.bot.d.localizer.get_text(
                        ctx, "cmd.play.added_to_queue.response"
                    ).format(
                        ctx.bot.d.localizer.get_text(
                            ctx, "generic.track_info_no_url"
                        ).format(
                            track.info.author,
                            track.info.title,
                            track.user_data["requester_id"],
                        )
                    )
                )
        # este else es para cuando se envia el enlace de una playlist
        else:
            tracks = loaded_tracks.tracks
            for i in tracks:
                i.user_data = {"requester_id": int(ctx.author.id)}
            # se añade la playlist a la cola
            queue = player_ctx.get_queue()
            queue.append(tracks)
            await ctx.respond(
                ctx.bot.d.localizer.get_text(
                    ctx, "cmd.play.added_playlist_to_queue.response"
                ).format(loaded_tracks.info.name)
            )

    # Error or no results
    # el else sale si hay un error o no se encuentran resultados
    else:
        try:
            # se busca la query en yt-dlp
            await play_yt_dlp(query, ctx, player_ctx, has_joined)
        # el except sale cuando la aplicación no soporta el url que se está dando
        except yt_dlp.UnsupportedUrl:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.play.url_not_supported")
            )
        # este except sale cuando hay un error distinto
        except Exception as e:
            logging.error(e)
            await ctx.respond(ctx.bot.d.localizer.get_text(ctx, "error.response"))
        return None
    # try_play reproduce la canción cuando es la primera vez que usas el comando !play
    await try_play(player_ctx, has_joined)
    return None


async def play_yt_dlp(
    query: str, ctx: Context, player_ctx: PlayerContext, has_joined: bool
):
    # el query.replace cambia la busqueda de spotify por la de youtube
    query = query.replace("spsearch", "ytsearch")
    # si no encuentra resultados con la busqueda en spotify...
    # el bot buscará en yt-dlp
    ytdl_query = {}

    # el metodo extract() extrae la información del resultado de la query
    def extract() -> t.Dict[str, t.Any]:
        info = ytdl.extract_info(query, download=False)
        return info  # type: ignore

    loop = asyncio.get_event_loop()

    ytdl_query = await loop.run_in_executor(None, extract)
    print(ytdl_query["url"])

    tracks = await ctx.bot.d.lavalink.load_tracks(ctx.guild_id, ytdl_query["url"])
    loaded_tracks = tracks.data
    if tracks.load_type == TrackLoadType.Track:
        valid = []
        for i in ytdl_query["formats"]:
            if not i.get("filesize_approx"):
                valid.append(i["url"])
        tracks = await ctx.bot.d.lavalink.load_tracks(ctx.guild_id, valid[-1])
        loaded_tracks = tracks.data

    if tracks.load_type != TrackLoadType.Track:  # tracks is empty
        raise Exception("Invalid API response")

    info = loaded_tracks.info

    info.title = ytdl_query.get("title") or ctx.bot.d.localizer.get_text(
        ctx, "cmd.play.yt-dlp.unknown_title"
    )
    info.author = ytdl_query.get("uploader") or ctx.bot.d.localizer.get_text(
        ctx, "cmd.play.yt-dlp.unknown_artist"
    )
    info.uri = ytdl_query.get("original_url")

    loaded_tracks.info = info
    loaded_tracks.user_data = {"requester_id": int(ctx.author.id),
                               "title": info.title,
                               "author": info.author,
                               "uri": info.uri}
    player_ctx.queue(loaded_tracks)

    if loaded_tracks.info.uri:
        await ctx.respond(
            ctx.bot.d.localizer.get_text(
                ctx, "cmd.play.added_to_queue.response"
            ).format(
                ctx.bot.d.localizer.get_text(ctx, "generic.track_info_url").format(
                    loaded_tracks.info.author,
                    loaded_tracks.info.title,
                    loaded_tracks.info.uri,
                    loaded_tracks.user_data["requester_id"],
                )
            )
        )
    else:
        await ctx.respond(
            ctx.bot.d.localizer.get_text(
                ctx, "cmd.play.added_to_queue.response"
            ).format(
                ctx.bot.d.localizer.get_text(ctx, "generic.track_info_no_url").format(
                    loaded_tracks.info.author,
                    loaded_tracks.info.title,
                    loaded_tracks.user_data["requester_id"],
                )
            )
        )
    # try_play reproduce la canción cuando es la primera vez que usas el comando !play
    await try_play(player_ctx, has_joined)
    return None


async def try_play(player_ctx: PlayerContext, has_joined: bool):
    player_data = await player_ctx.get_player()

    if player_data:
        if (
            not player_data.track
            and await player_ctx.get_queue().get_queue()
            and not has_joined
        ):
            player_ctx.skip()


@plugin.command()
@lightbulb.command(
    "skip",
    "Skip the currently playing song",
    auto_defer=True,
    name_localizations={hikari.Locale.ES_ES: "saltar"},
    description_localizations={
        hikari.Locale.ES_ES: "Salta la canción que se está reproduciendo " "actualmente"
    },
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def skip(ctx: Context) -> None:
    """Skip the currently playing song"""
    if not ctx.guild_id:
        return None
    # miramos si el bot ya está conectado en un canal
    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(
            ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response")
        )
        return None
    # isinstance mira si voice es una instancia de LavalinkVoice
    assert isinstance(voice, LavalinkVoice)
    # player es el reproductor de musica que usa el bot cuando se une a un canal de voz
    player = await voice.player_ctx.get_player()
    # si se está reproduciendo una canción el bot introducirá en un mensaje la canción que ha saltado,
    # con la información de esta
    if player.track:
        if player.track.info.uri:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.skip.skipped.response").format(
                    ctx.bot.d.localizer.get_text(ctx, "generic.track_info_url").format(
                        player.track.info.author,
                        player.track.info.title,
                        player.track.info.uri,
                        player.track.user_data["requester_id"],
                    )
                )
            )
        else:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.skip.skipped.response").format(
                    ctx.bot.d.localizer.get_text(
                        ctx, "generic.track_info_no_url"
                    ).format(
                        player.track.info.author,
                        player.track.info.title,
                        player.track.user_data["requester_id"],
                    )
                )
            )
        # el bot salta a la siguiente canción en la cola
        voice.player_ctx.skip()
    # si no hay ninguna canción reproduciendose entonces pondrá un mensaje diciendolo
    else:
        await ctx.respond(
            ctx.bot.d.localizer.get_text(ctx, "cmd.skip.nothing_skip.response")
        )


@plugin.command()
@lightbulb.command(
    "stop",
    "Stop the currently playing song",
    auto_defer=True,
    name_localizations={hikari.Locale.ES_ES: "parar"},
    description_localizations={
        hikari.Locale.ES_ES: "Para la canción que se está reproduciendo " "actualmente"
    },
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def stop(ctx: Context) -> None:
    """Stop the currently playing song"""
    if not ctx.guild_id:
        return None
    # miramos si el bot ya está conectado en un canal
    voice = ctx.bot.voice.connections.get(ctx.guild_id)

    if not voice:
        await ctx.respond(
            ctx.bot.d.localizer.get_text(ctx, "cmd.error.no_voice.response")
        )
        return None
    # isinstance mira si voice es una instancia de LavalinkVoice
    assert isinstance(voice, LavalinkVoice)
    # player es el reproductor de musica que usa el bot cuando se une a un canal de voz
    player = await voice.player_ctx.get_player()
    # si se está reproduciendo una canción el bot introducirá en un mensaje la canción que ha parado,
    # con la información de esta
    if player.track:
        if player.track.info.uri:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.stop.stopped.response").format(
                    ctx.bot.d.localizer.get_text(ctx, "generic.track_info_url").format(
                        player.track.info.author,
                        player.track.info.title,
                        player.track.info.uri,
                        player.track.user_data["requester_id"],
                    )
                )
            )
        else:
            await ctx.respond(
                ctx.bot.d.localizer.get_text(ctx, "cmd.stop.stopped.response").format(
                    ctx.bot.d.localizer.get_text(
                        ctx, "generic.track_info_no_url"
                    ).format(
                        player.track.info.author,
                        player.track.info.title,
                        player.track.user_data["requester_id"],
                    )
                )
            )
        # para la canción
        await voice.player_ctx.stop_now()
    else:
        await ctx.respond(
            ctx.bot.d.localizer.get_text(ctx, "cmd.stop.nothing_stop.response")
        )


def load(bot: GatewayBot) -> None:
    bot.add_plugin(plugin)
