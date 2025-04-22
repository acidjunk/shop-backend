from uuid import UUID

import httpx

from server.schemas.order import OrderUpdated
from server.utils.discord.settings import DiscordSettings


def post_discord_info_request(content: str, settings: DiscordSettings, email: str, product_name: str, product_id: UUID):
    # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    data = {
        "content": content,
        "username": settings.BOT_NAME,
        "embeds": [
            {
                "title": "New Info Request!",
                "description": f"**Email:** {email}\n**Product:** {product_name}\n**Product Link:** {settings.PRODUCT_BASE_URL}{product_id}",
            }
        ],
    }

    result = httpx.post(settings.WEBHOOK_URL, json=data)
    result.raise_for_status()


def post_discord_order_complete(content: str, settings: DiscordSettings, order: OrderUpdated, email: str):
    # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    data = {
        "content": content,
        "username": settings.BOT_NAME,
        "embeds": [
            {
                "title": f"New Order! See at https://editor.shopvirge.com/orders",
                "description": f"**Customer Email:** {email}\n **Order Number:** {order.customer_order_id}\n **Total:** {order.total}",
            }
        ],
    }

    result = httpx.post(settings.WEBHOOK_URL, json=data)
    result.raise_for_status()


if __name__ == "__main__":
    post_discord_info_request("All your base are belong to us!")
