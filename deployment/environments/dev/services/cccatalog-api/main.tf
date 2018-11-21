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
  name_suffix               = ""
  environment               = "dev"
  min_size                  = 3
  max_size                  = 3
  instance_type             = "t2.small"
  enable_monitoring         = false
  git_revision              = "b3998e4eb7f0e14c4ac1fb588e05f8a3802509a7"
  api_version               = "0.18.0"

  # Environment-specific variables
  database_host             = "ccsearch-intermediary-db.ctypbfibkuqv.us-east-1.rds.amazonaws.com"
  django_debug_enabled      = "False"
  elasticsearch_port        = "80"
  aws_region                = "us-east-1"
  elasticsearch_url         = "search-cccatalog-es-prod4-200mm-o22hjpa5hxct6qawt6bqk4oo7a.us-east-1.es.amazonaws.com"
  redis_host                = "ip-172-30-1-215.ec2.internal"
  ccc_api_host              = "api-dev.creativecommons.engineering"
  root_shortening_url       = "dev.shares.cc"
  #disable_global_throttling = "True"

  # Secrets not checked into version control. Override with -var-file=secrets.tfvars
  database_password         = "${var.database_password}"
  django_secret_key         = "${var.django_secret_key}"
  wsgi_auth_credentials     = "${var.wsgi_auth_credentials}"
  aws_access_key_id         = "${var.aws_access_key_id}"
  aws_secret_access_key     = "${var.aws_secret_access_key}"
  redis_password            = "${var.redis_password}"
}
