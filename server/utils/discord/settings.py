from server.schemas.base import BoilerplateBaseModel


class DiscordSettings(BoilerplateBaseModel):
    BOT_NAME: str
    WEBHOOK_URL: str
    SHOP_ID: str
    PRODUCT_BASE_URL: str


co2_shop_settings = DiscordSettings(
    BOT_NAME="CO2 Tree Shop Bot",
    WEBHOOK_URL="https://discord.com/api/webhooks/1362881370137034752/g1Xrt6z08I1n8CUFy2iGDoxmvsms-hlVuvCYd2DPScfhfL0eq3kzsrQUYTiSt0jrVpn9",
    SHOP_ID="d3c745bc-285f-4810-9612-6fbb8a84b125",
    PRODUCT_BASE_URL="https://editor.shopvirge.com/product/form/",
)
