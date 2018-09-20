provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "63c6ee73ad569b8d0483c00b1fd0535ec6cebbbf"
  instance_type             = "t2.small"
  api_url                   = "https://api.creativecommons.engineering"
}
