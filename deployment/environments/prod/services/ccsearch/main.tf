provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "706fce6212411fc30d7fecdef0309eb665e157a7"
  instance_type             = "t2.small"
  api_url                   = "https://api.creativecommons.engineering"
}
