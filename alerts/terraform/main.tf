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


data "aws_ecr_image" "send-alert-image" {
  repository_name = "c16-energy-send-alerts"
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

data "aws_iam_policy_document" "lambda-ses-policy" {
  statement {
    effect = "Allow"
    actions = [
      "ses:SendEmail",
      "ses:SendRawEmail"
    ]
    resources = ["arn:aws:ses:eu-west-2:*:identity/*"]
  }
}


resource "aws_iam_role" "energy-alerts-lambda-iam" {
  name               = "c16-energy-send-alerts-lambda-iam"
  assume_role_policy = data.aws_iam_policy_document.assume-role.json
}

resource "aws_iam_role_policy" "lambda-logs-policy" {
  name   = "lambda-logs"
  role   = aws_iam_role.energy-alerts-lambda-iam.id
  policy = data.aws_iam_policy_document.lambda-logging.json
}

resource "aws_iam_role_policy" "lambda-ses-policy" {
  name   = "lambda-ses-policy"
  role   = aws_iam_role.energy-alerts-lambda-iam.id
  policy = data.aws_iam_policy_document.lambda-ses-policy.json
}

resource "aws_lambda_function" "energy-alerts-lambda" {
  function_name = "c16-energy-send-alerts-lambda"
  image_uri = data.aws_ecr_image.send-alert-image.image_uri

  role = aws_iam_role.energy-alerts-lambda-iam.arn
  package_type = "Image"
  environment {
    variables = {
                DB_NAME = var.DB_NAME,
                DB_USER = var.DB_USER,
                DB_HOST = var.DB_HOST,
                DB_PORT = var.DB_PORT,
                DB_PASSWORD = var.DB_PASSWORD,
                SENDER_EMAIL = var.SENDER_EMAIL

    }
  }
  timeout = 60
}