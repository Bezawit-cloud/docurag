from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    groq_api_key: str
    upgrade_url: str = "https://your-landing-page.com/pricing"

    class Config:
        env_file = ".env"

settings = Settings()