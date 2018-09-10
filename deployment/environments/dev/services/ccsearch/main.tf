provider "aws" {
  region = "us-east-1"
}

module "ccsearch" {
  source = "../../../../modules/services/ccsearch"

  vpc_id                    = "vpc-b741b4cc"
  environment               = "-dev"
  git_revision              = "35331eab680c362a8edc7e7d371b742f0ed2736f"
  instance_type             = "t2.small"
  api_url                   = "https://api-dev.creativecommons.engineering"
}
