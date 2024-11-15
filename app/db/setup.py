from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticClient
from ..core.config import settings as s
import boto3
from loguru import logger  # Import Loguru logger

CERT_CACHE_PATH = 'cert.pem'
DEV = True
# Global client instance
_client: AgnosticClient = None


def download_cert_from_s3():
    try:
        s3 = boto3.client('s3')
        bucket_name = s.bucket_name
        cert_file_key = s.path_to_cert
        response = s3.get_object(Bucket=bucket_name, Key=cert_file_key)
        cert_data = response['Body'].read()
        # Write the certificate to the cache path
        with open(CERT_CACHE_PATH, 'wb') as cert_file:
            cert_file.write(cert_data)
    except Exception as e:
        logger.error("Failed to download certificate from S3: %s", e)
        raise


def build_connection_options():
    options = ""
    if s.database_tls:
        download_cert_from_s3()
        options += f"&tls={s.database_tls}&tlsCAFile={CERT_CACHE_PATH}"
    if s.replica_set:
        # Added "&" for proper formatting
        options += f"&replicaSet={s.replica_set}"

    if DEV:
        options += f"&tlsAllowInvalidCertificates=true"
        options += f"&directConnection=true"
    return options


def add_credentials():
    if s.database_username and s.database_password:
        return f"{s.database_username}:{s.database_password}"
    return ""


def build_uri():
    if not s.database_hostname or not s.database_port:
        raise ValueError("Database hostname and port must be specified")

    uri = f"{s.database_hostname}:{s.database_port}"
    access = add_credentials()
    if access:
        uri = f"{access}@{uri}"

    options = build_connection_options()
    uri = uri + "/?" + (f"{options}" if options else "").lstrip("&")
    return f"mongodb://{uri}"


# @lru_cache
def get_client() -> AgnosticClient:
    """Create and cache MongoDB client."""
    global _client
    if not _client:
        uri = build_uri()
        _client = AsyncIOMotorClient(uri)
    logger.debug(f"Client : {id(_client)}")
    return _client
