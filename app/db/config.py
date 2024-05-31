from motor.motor_asyncio import AsyncIOMotorClient
from ..utils.config import settings as s
from functools import lru_cache
import boto3

credentials = "{username}:{password}"
uri_template = "mongodb://{hostname}:{port}"

def download_cert_from_s3():
    try:
        s3 = boto3.client('s3')
        bucket_name = s.bucket_name
        cert_file_key = s.path_to_cert
        cert_cache_path = '/tmp/cert.pem'
        response = s3.get_object(Bucket=bucket_name, Key=cert_file_key)
        cert_data = response['Body'].read()
        
        # Write the certificate to the cache path
        with open(cert_cache_path, 'wb') as cert_file:
            cert_file.write(cert_data)
    except Exception as e:
        print(e)
        raise e
    
def define_options():
    options = "/?"
    if s.database_tls:
        download_cert_from_s3()
        options += "tls={}&tlsCAFile={}".format(s.database_tls, s.database_tls_ca_filename)
    if s.replica_set:
        options += "replicaSet={}".format(s.replica_set)
    return options

def add_credentials():
    if s.database_username and s.database_password:
        credentials.format(
            s.database_username,
            s.database_password)
        return credentials
    return None

def build_uri():
    uri = uri_template.format(
        hostname=s.database_hostname,
        port=s.database_port
        )
    access = add_credentials()
    options = define_options()
    if access:
        uri = access + "@" + uri
    uri = uri + options
    return uri

@lru_cache()
def get_client():
    """Create and cache MongoDB client."""
    print(s.database_username)
    uri = build_uri()
    print(uri)
    return AsyncIOMotorClient(uri)
