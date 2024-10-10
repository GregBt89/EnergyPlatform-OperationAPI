def get_pymongo_client():
    import pymongo
    # Create a MongoDB client, open a connection to Amazon DocumentDB as a replica set and specify the read preference as secondary preferred
    try:
        client = pymongo.MongoClient(
            'mongodb://indigenerAdmin:U49WPr6hMSGvRVS@localhost:27018/?tls=true&tlsCAFile=aws_debug/global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&tlsAllowInvalidCertificates=true&directConnection=true')

        print("Successfully connected to MongoDB")

        # List databases to test the connection
        databases = client.list_database_names()
        print("Connected to the following databases:", databases)

        return client
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("Could not connect to MongoDB:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)


if __name__ == "__main__":
    client = get_pymongo_client()
    # print(dir(client))
    print(client.list_database_names())
    # Close the connection
    client.close()
