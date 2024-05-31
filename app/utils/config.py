from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    database_tls : Optional[str]
    database_tls_ca_filename: Optional[str]
    bucket_name: Optional[str] 
    path_to_cert: Optional[str]

    class Config:
        env_file=".env"

settings = Settings()
