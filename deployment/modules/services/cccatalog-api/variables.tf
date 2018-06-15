variable "vpc_id" {
  description = "The ID of the VPC to initialize terraform resources inside of."
}

variable "environment" {
  description = "The staging environment of a deployment, typically 'dev' or 'prod'."
}

variable "min_size" {
  description = "The minimum number of API server autoscaled instances."
  default     = 1
}

variable "max_size" {
  description = "The maximum number of API server autoscaled instances."
  default     = 5
}

variable "instance_type" {
  description = "The EC2 instance type of API server autoscaled instances."
  default     = "t2.micro"
}

variable "enable_monitoring" {
  description = "Whether CloudWatch is enabled for the API server autoscaling launch configuration."
  default     = "false"
}

variable "database_host" {
  description = "The hostname of the PostgreSQL server to connect to."
}

variable "database_password" {
  description = "The password of the PostgreSQL server."
}

variable "django_debug_enabled" {
  description = "Whether Django debug mode is enabled. Must be disabled in production."
  default     = "false"
}

variable "django_secret_key" {
  description = "The secret Django key used for miscellaneous authorization tasks."
}

  description = "The git commit hash to deploy."
}

variable "wsgi_auth_credentials" {
  # Example: "username:password"
  description = "If defined, the API server will restrict access to all endpoints (except /healthcheck) with basic auth."
  default = ""
}