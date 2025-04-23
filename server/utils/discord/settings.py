from pydantic_settings import BaseSettings


class DiscordSettings(BaseSettings):
    BOT_NAME: str = "CO2 Tree Shop Bot"
    WEBHOOK_URL: str = "CHANGEME"
    SHOP_ID: str = "d3c745bc-285f-4810-9612-6fbb8a84b125"
    PRODUCT_BASE_URL: str = "https://editor.shopvirge.com/product/form/"


co2_shop_settings = DiscordSettings()
