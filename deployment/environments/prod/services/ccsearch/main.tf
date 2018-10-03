provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "c889f9e68ea0823e3b22aaa9a7bc4f24e4402833"
  instance_type             = "t2.small"
  api_url                   = "https://api.creativecommons.engineering"
}
