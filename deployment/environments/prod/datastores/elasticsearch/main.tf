provider "aws" {
  region = "us-east-1"
}

resource "aws_elasticsearch_domain" "elasticsearch-prod" {
  domain_name           = "cccatalog-elasticsearch-prod"
  elasticsearch_version = "6.2"
N
  cluster_config {
    instance_type            = "m4.large.elasticsearch"
    dedicated_master_count   = "3"
    dedicated_master_enabled = "true"
    dedicated_master_type    = "m3.medium.elasticsearch"
    instance_count           = "3"
  }

  advanced_options {
    "rest.action.multi.allow_explicit_index" = "true"
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "standard"
    volume_size = 30
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
      "Resource": "arn:aws:es:us-east-1:664890800379:domain/cccatalog-elasticsearch-prod/*"
    }
  ]
}
EOF
}
