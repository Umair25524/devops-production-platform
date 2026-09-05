terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

resource "aws_instance" "app" {
  ami                         = "ami-094210f044117049d"
  instance_type               = "c7i-flex.large"
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.app.id]
  key_name                    = "devops-production-key"
  associate_public_ip_address = true

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name        = "devops-production-server"
    Environment = "learning"
    Project     = "devops-production-platform"
  }
}