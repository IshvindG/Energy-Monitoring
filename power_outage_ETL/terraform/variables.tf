variable "DB_USER" {
  type = string
  description = "SQL Server Database username"
}

variable "DB_PASSWORD" {
  type = string
  description = "SQL Server Database password"
  sensitive = true
}

variable "DB_HOST" {
  type = string
  description = "SQL Server Database host"
}

variable "DB_NAME" {
  type = string
  description = "SQL Server Database name"
}

variable "DB_PORT" {
  type = string
  description = "SQL Server Database port"
}

variable "existing_vpc_name" {
  type = string
  description = "VPC Name"
}