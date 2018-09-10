provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "3b7f2306f1faa7a7ca728ddb112e66bea7a6c065"
  instance_type             = "t2.small"
}
