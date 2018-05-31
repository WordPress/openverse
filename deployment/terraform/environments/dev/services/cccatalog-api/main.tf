provider "aws" {
  region = "us-west-1"
}

# Variables passed in from the secrets file get declared here.
variable "database_password" {
  type = "string"
}
variable "django_secret_key" {
  type = "string"
}

module "cccatalog-api" {
  source = "../../../../modules/services/cccatalog-api"

  environment               = "dev"
  min_size                  = 2
  max_size                  = 5
  instance_type             = "t2.micro"
  enable_monitoring         = false
  git_revision              = "122978f1bf84aae3033c8bb603aa6c666af08f18"

  # Environment-specific variables
  database_host             = "openledger-db-dev3-nvirginia.ctypbfibkuqv.us-east-1.rds.amazonaws.com"
  django_debug_enabled      = "true"

  # Secrets not checked into version control. Override with -var-file=secrets.tfvars
  database_password         = "${var.database_password}"
  django_secret_key         = "${var.django_secret_key}"
}
