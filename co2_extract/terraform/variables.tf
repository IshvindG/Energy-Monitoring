variable "DB_USERNAME" {
  type = string
  description = "RDS username"
}

variable "DB_PASSWORD" {
  type = string
  description = "RDS password"
  sensitive = true
}

variable "DB_HOST" {
  type = string
  description = "RDS host"
}

variable "DB_NAME" {
  type = string
  description = "RDS name"
}

variable "DB_PORT" {
  type = string
  description = "RDS port"
}