provider "aws" {
  region = "us-east-1"
}

# Variables passed in from the secrets file get declared here.
variable "redis_password" {
  type = "string"
}

module "cacheserver" {
  source         = "../../../../modules/services/cacheserver"
  redis_password = "${var.redis_password}"
  instance_type  = "t2.small"
  environment    = "dev"
  vpc_id         = "vpc-b741b4cc"
}
