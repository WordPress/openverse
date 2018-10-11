provider "aws" {
  region = "us-east-1"
}

# Variables passed in from the secrets file get declared here.
variable "database_password" {
  type = "string"
}
variable "django_secret_key" {
  type = "string"
}
variable "wsgi_auth_credentials" {
  type = "string"
}
variable "aws_access_key_id" {
  type = "string"
}
variable "aws_secret_access_key" {
  type = "string"
}
variable "redis_password" {
  type = "string"
}

module "cccatalog-api" {
  source = "../../../../modules/services/cccatalog-api"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  min_size                  = 3
  max_size                  = 3
  instance_type             = "c5d.xlarge"
  enable_monitoring         = false
  git_revision              = "618638abb5240464f9d821ae51189666a7d6a0ef"
  api_version               = "0.17.2"

  # Environment-specific variables
  database_host             = "production-api-v0-17.ctypbfibkuqv.us-east-1.rds.amazonaws.com"
  django_debug_enabled      = "false"
  elasticsearch_port        = "80"
  aws_region                = "us-east-1"
  elasticsearch_url         = "search-cccatalog-es-prod3-of6oi33xtrsxp63mxuc47nhxeu.us-east-1.es.amazonaws.com"
  redis_host                = "ip-172-30-1-251.ec2.internal"
  ccc_api_host              = "api.creativecommons.engineering"
  root_shortening_url       = "shares.cc"

  # Secrets not checked into version control. Override with -var-file=secrets.tfvars
  database_password         = "${var.database_password}"
  django_secret_key         = "${var.django_secret_key}"
  wsgi_auth_credentials     = "${var.wsgi_auth_credentials}"
  aws_access_key_id         = "${var.aws_access_key_id}"
  aws_secret_access_key     = "${var.aws_secret_access_key}"
  redis_password            = "${var.redis_password}"
}
