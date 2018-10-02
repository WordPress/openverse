provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "247cedd5b68b15ce4c2b660840dc3d62063c44ba"
  instance_type             = "t2.small"
  api_url                   = "https://api.creativecommons.engineering"
}
