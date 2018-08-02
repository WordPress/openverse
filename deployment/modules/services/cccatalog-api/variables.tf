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

variable "git_revision"{
  description = "The git commit hash to deploy."
}

variable "wsgi_auth_credentials" {
  # Example: "username:password"
  description = "If defined, the API server will restrict access to all endpoints (except /healthcheck) with basic auth."
  default = ""
}

variable "aws_access_key_id" {
  description = "The access key ID used to connect to Elasticsearch."
}

variable "aws_secret_access_key" {
  description = "The secret access key used to connect to Elasticsearch."
}

variable "elasticsearch_url" {
  description = "The URL of the Elasticsearch instance to synchronize."
}

variable "elasticsearch_port" {
  description = "The port used to connect to Elasticsearch."
}

variable "aws_region" {
  description = "The region of the Elasticsearch instance. Required for IAM auth."
}

variable "api_version" {
  description = "The current version of the API. Expected to use the semantic version format. X.Y.Z+<SHA COMMIT HASH>. The commit hash is appended for you automatically. \nMore details: https://semver.org/. \n\nExample: 0.1.0"
}

variable "redis_host" {
  description = "Cache server hostname"
}

variable "redis_password" {
  description = "Cache server password"
}

variable "ccc_api_host" {
  description = "The hostname of the API server. Used by the URL shortener proxy to locate /link endpoint."
}