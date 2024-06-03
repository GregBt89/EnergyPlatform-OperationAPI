@echo off
cd aws_deploy/
aws cloudformation update-stack --stack-name indigener-op-istentore-dev-api --template-body file://template.yaml --capabilities CAPABILITY_IAM
cd ..
