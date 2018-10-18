provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-prod"
  git_revision              = "9a743394fd098999492619f522c1445d4bd6587a"
  instance_type             = "t2.small"
  api_url                   = "https://api.creativecommons.engineering"
}
