@echo off
cd aws_deploy/
aws cloudformation create-stack --stack-name indigener-op-istentore-dev-api --template-body file://template.yaml --capabilities CAPABILITY_IAM --parameters ParameterKey=APINameDNS,ParameterValue=istentore.operation.dev.api ParameterKey=APIDockerImageECR,ParameterValue='753332115423.dkr.ecr.eu-central-1.amazonaws.com/indigener-operation-api:istentore_3.0.0' ParameterKey=ECSServiceName,ParameterValue=indigener-istentore-operation-api ParameterKey=APIS3EnvFilesARN,ParameterValue='arn:aws:s3:::indigener/apis/istentore/operation_v3.env'
cd ..