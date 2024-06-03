@echo on
ssh -v -i "bastion-host.pem" -L 8010:istentore.operation.dev.api.backend.indigener:8000 ec2-user@ec2-35-156-152-81.eu-central-1.compute.amazonaws.com