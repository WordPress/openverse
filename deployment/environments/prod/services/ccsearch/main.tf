provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "84934ad3fadffaad4730f5a3ff44a02c236371df"
  instance_type             = "t2.small"
  api_url                   = "https://api.creativecommons.engineering"
}
