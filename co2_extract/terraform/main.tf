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


data "aws_ecr_image" "energy-co2-pipeline-image" {
  repository_name = "c16-energy-co2-pipeline"
  image_tag = "latest"
}

data "aws_iam_policy_document" "assume-role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole"
      ]
      
  }
}

data "aws_iam_policy_document" "lambda-logging" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}


resource "aws_iam_role" "energy-co2-info-lambda-iam" {
  name               = "c16-energy-co2-info-lambda-iam"
  assume_role_policy = data.aws_iam_policy_document.assume-role.json
}

resource "aws_iam_role_policy" "lambda-logs-policy" {
  name   = "lambda-logs"
  role   = aws_iam_role.energy-co2-info-lambda-iam.id
  policy = data.aws_iam_policy_document.lambda-logging.json
}


resource "aws_lambda_function" "energy-co2-lambda" {
  function_name = "c16-energy-co2-lambda"
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c16-energy-co2-pipeline:latest"
  
  role          = aws_iam_role.energy-co2-info-lambda-iam.arn
  package_type  = "Image"
  environment {
    variables = {
                DB_NAME = var.DB_NAME,
                DB_USERNAME = var.DB_USER,
                DB_HOST = var.DB_HOST,
                DB_PORT = var.DB_PORT,
                DB_PASSWORD = var.DB_PASSWORD

    }
  }
  timeout = 60
}