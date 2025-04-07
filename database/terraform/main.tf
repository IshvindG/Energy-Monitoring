terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "~> 5.93.0"
    }
  }
}

provider "aws" {
    region = "eu-west-2"
}

data "aws_vpc" "c16-vpc"{
    filter {
      name = "tag:Name"
      values = [var.existing_vpc_name]
    }
}

resource "aws_security_group" "energy-db-sg" {
    name = "c16-energy-db-sg"
    description = "Security Group for Energy DB"
    tags = {
      Name = "c16-energy-db-sg"
    }
    vpc_id = data.aws_vpc.c16-vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "mssql" {
  security_group_id = aws_security_group.energy-db-sg.id
  ip_protocol = "tcp"
  from_port = 5432
  to_port = 5432
  cidr_ipv4 = "0.0.0.0/0"
}


resource "aws_vpc_security_group_egress_rule" "all_traffic" {
  ip_protocol = "-1"
  security_group_id = aws_security_group.energy-db-sg.id
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_db_instance" "c16-energy-db" {
    db_name = "energy"
    identifier = "c16-energy-db"
    engine = "postgres"
    engine_version = "17.2"
    instance_class = "db.t3.micro"
    vpc_security_group_ids = [aws_security_group.energy-db-sg.id]
    db_subnet_group_name = var.existing_db_subnet
    publicly_accessible = true
    skip_final_snapshot = true
    allocated_storage = 20
    performance_insights_enabled = false
    username = var.db_username
    password = var.db_password
}

output "db_ip_addr" {
  description = "DB Address"
  value = aws_db_instance.c16-energy-db.endpoint
}