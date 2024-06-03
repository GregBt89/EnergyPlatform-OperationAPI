@echo off
cd ..
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 753332115423.dkr.ecr.eu-central-1.amazonaws.com
docker build -t op_api_istentore:3.0.0 .
docker tag op_api_istentore:3.0.0 753332115423.dkr.ecr.eu-central-1.amazonaws.com/indigener-operation-api:istentore_3.0.0
docker push 753332115423.dkr.ecr.eu-central-1.amazonaws.com/indigener-operation-api:istentore_3.0.0
