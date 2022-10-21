from pydantic import BaseSettings


class Settings(BaseSettings):
    redis_host="some default string value" # default value if env variable does not exist
    mongodb_conn_string: str

# specify .env file location as Config attribute
    class Config:
        env_file = ".env"