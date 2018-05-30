provider "aws" {
  region = "us-west-1"
}

module "cccatalog-api" {
  source = "../../../../modules/services/cccatalog-api"

  environment       = "dev"
  min_size          = 2
  max_size          = 5
  instance_type     = "t2.micro"
  enable_monitoring = false

  # Environment-specific variables
  database_host     = "openledger-db-dev3-nvirginia.ctypbfibkuqv.us-east-1.rds.amazonaws.com"
  # Secrets not checked into version control. Override with -var-file=secrets.tfvars
  database_password = ""
}
