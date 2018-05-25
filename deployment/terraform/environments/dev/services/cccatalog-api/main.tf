provider "aws" {
  region = "us-west-1"
}

module "cccatalog-api" {
  source = "../../../../modules/services/cccatalog-api"

  environment   = "dev"
  min_size      = 1
  max_size      = 5
  instance_type = "t2.micro"
}
