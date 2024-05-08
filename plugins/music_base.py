import locale
import os
import logging
import typing as t

import hikari
import lightbulb
import lavalink_rs
from hikari import GatewayBot
from lightbulb import Plugin
from lavalink_rs.model import events

plugin = Plugin("Music (base) events")
plugin.add_checks(lightbulb.guild_only)


class Events(lavalink_rs.EventHandler):
    # el evento ready aparece cuando el bot se conecta correctamente a lavalink
    async def ready(
        self,
        client: lavalink_rs.LavalinkClient,
        session_id: str,
        event: events.Ready,
    ) -> None:
        del client, session_id, event
        logging.info("HOLY READY")

    # el evento track_start cuando empieza una canción
    async def track_start(
        self,
        client: lavalink_rs.LavalinkClient,
        session_id: str,
        event: events.TrackStart,
    ) -> None:
        del session_id

        logging.info(
            f"Started track {event.track.info.author} - {event.track.info.title} in {event.guild_id.inner}"
        )

        player_ctx = client.get_player_context(event.guild_id.inner)

        assert player_ctx
        assert player_ctx.data

        data = player_ctx.data

        if event.track.info.uri:
            await data[1].rest.create_message(
                data[0],
                data[1].d.localizer.get_text(data[2], "event.track_start.response").format(
                    data[1].d.localizer.get_text(data[2], "generic.track_info_url").format(
                        event.track.info.author,
                        event.track.info.title,
                        event.track.info.uri,
                        event.track.user_data["requester_id"],
                    )
                ),
            )
        else:
            await data[1].rest.create_message(
                data[0],
                data[1].d.localizer.get_text(data[2], "event.track_start.response").format(
                    data[1].d.localizer.get_text(data[2], "generic.track_info_no_url").format(
                        event.track.info.author,
                        event.track.info.title,
                        event.track.user_data["requester_id"],
                    )
                ),
            )

        if client.data and event.guild_id in client.data:
            queue_ref = player_ctx.get_queue()
            queue_ref.push_to_front(event.track)


@plugin.listener(hikari.ShardReadyEvent, bind=True)
async def start_lavalink(plug: Plugin, event: hikari.ShardReadyEvent) -> None:
    """Event that triggers when the hikari gateway is ready."""

    node = lavalink_rs.NodeBuilder(
        "lavalink.vicky.rs:2333",
        False,  # is the server SSL?
        os.environ["LAVALINK_PASSWORD"],
        event.my_user.id,
    )

    lavalink_client = await lavalink_rs.LavalinkClient.new(
        Events(),
        [node],
        lavalink_rs.NodeDistributionStrategy.sharded(),
    )

    plug.bot.d.lavalink = lavalink_client


def load(bot: GatewayBot) -> None:
    bot.add_plugin(plugin)
