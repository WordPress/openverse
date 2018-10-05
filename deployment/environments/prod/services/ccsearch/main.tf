provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "1997583310568cb8a105f557cc3966ca2f57698b"
  instance_type             = "t2.small"
  api_url                   = "https://api.creativecommons.engineering"
}
