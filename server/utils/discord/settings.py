from pydantic_settings import BaseSettings


class DiscordSettings(BaseSettings):
    BOT_NAME: str
    WEBHOOK_URL: str
    PRODUCT_BASE_URL: str = "https://editor.shopvirge.com/product/form/"
