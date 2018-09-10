provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "2aef862f0697d3808d6b3e049a4d21242b10236a"
  instance_type             = "t2.small"
  api_url                   = "https://api.creativecommons.engineering"
}
