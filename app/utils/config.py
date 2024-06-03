from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: Optional[str]=None
    database_name: str
    database_username: Optional[str]=None
    database_tls : Optional[str]
    database_tls_ca_filename: Optional[str]
    bucket_name: Optional[str] 
    path_to_cert: Optional[str]
    replica_set: Optional[str]=None
    uvicorn_host: Optional[str]='0.0.0.0'
    uvicorn_port: Optional[str]='8000'
    uvicorn_workers: Optional[int]=2

    class Config:
        env_file=".env"

settings = Settings()
