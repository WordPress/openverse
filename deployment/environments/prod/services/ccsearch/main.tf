provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "82a7209335fb8d3fe7e6c59f733229772c7feedc"
  instance_type             = "t2.small"
  api_url                   = "https://api.creativecommons.engineering"
}
