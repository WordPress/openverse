provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "378e98051ba6a3f4de95ae893ab7a8bef972b03c"
  instance_type             = "t2.small"
  api_url                   = "https://api.creativecommons.engineering"
}
