provider "aws" {
  region = "us-west-1"
}

resource "aws_elasticsearch_domain" "elasticsearch-dev" {
  domain_name           = "cc-search-large-8"
  elasticsearch_version = "5.3"

  cluster_config {
    instance_type            = "m4.large.elasticsearch"
    dedicated_master_count   = "3"
    dedicated_master_enabled = "true"
    dedicated_master_type    = "m4.large.elasticsearch"
    instance_count           = "3"
  }

  advanced_options {
    "rest.action.multi.allow_explicit_index" = "true"
  }

  access_policies = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::664890800379:user/openledger"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:us-west-1:664890800379:domain/cc-search-large-8/*"
    }
  ]
}
EOF
}
