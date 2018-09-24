provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "3357104502b433137d6b226d68a90abbe67bdef8"
  instance_type             = "t2.small"
  api_url                   = "https://api.creativecommons.engineering"
}
