terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "~> 5.92.0"
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

data "aws_ecs_cluster" "c16-ecs-cluster" {
  cluster_name = "c16-ecs-cluster"
}

data "aws_subnets" "c16-subnets" {
filter {
    name   = "tag:Name"
    values = ["c16-public-subnet-1", "c16-public-subnet-2", "c16-public-subnet-3"]
  }
}

resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name = "/ecs/c16-energy-outage-pipeline"
}

resource "aws_ecs_task_definition" "service" {
  family                   = "c16-power-outage-pipeline"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 3072
  execution_role_arn       = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"

  container_definitions = jsonencode([
    {
      name      = "energy-power-outage-pipeline"
      image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c16-energy-power-outage-pipeline:latest"
      cpu       = 0
      essential = true

      environment = [
        {
          name  = "DB_NAME"
          value = var.DB_NAME
        },
        {
          name  = "DB_USER"
          value = var.DB_USER
        },
        {
          name  = "DB_HOST"
          value = var.DB_HOST
        },
        {
          name  = "DB_PORT"
          value = var.DB_PORT
        },
        {
          name  = "DB_PASSWORD"
          value = var.DB_PASSWORD
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_log_group.name
          "awslogs-region"        = "eu-west-2"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}


resource "aws_security_group" "energy-outage-pipeline-sg" {
    name = "c16-energy-outage-pipeline-sg"
    description = "Security Group for C16 Power Outage Pipeline"
    tags = {
      Name = "c16-energy-power-outage-sg"
    }
    vpc_id = data.aws_vpc.c16-vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.energy-outage-pipeline-sg.id
  ip_protocol = "tcp"
  from_port = 5432
  to_port = 5432
  cidr_ipv4 = "0.0.0.0/0"
}


resource "aws_vpc_security_group_egress_rule" "all_traffic" {
  ip_protocol = "-1"
  security_group_id = aws_security_group.energy-outage-pipeline-sg.id
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_ecs_service" "c16-energy-power-outage-live-pipeline" {
  name = "c16-energy-power-outage-live-pipeline-${terraform.workspace}"
  cluster = data.aws_ecs_cluster.c16-ecs-cluster.id
  task_definition = aws_ecs_task_definition.service.arn
  desired_count = 1
  launch_type = "FARGATE"
  network_configuration {
    assign_public_ip = true
    security_groups = [ aws_security_group.energy-outage-pipeline-sg.id ]
    subnets = data.aws_subnets.c16-subnets.ids
  }
}

output "ip" {
  value = aws_ecs_service.c16-energy-power-outage-live-pipeline.network_configuration
}