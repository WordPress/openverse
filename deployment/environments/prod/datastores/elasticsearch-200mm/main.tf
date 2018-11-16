# A temporary cluster for the purpose of reindexing data without downtime.
# Once the data has been reindexed, it will be used as the main cluster.

provider "aws" {
  region = "us-east-1"
}

resource "aws_elasticsearch_domain" "elasticsearch-prod-clone" {
  domain_name           = "cccatalog-es-prod4-200mm"
  elasticsearch_version = "6.2"
  cluster_config {
    instance_type            = "m4.4xlarge.elasticsearch"
    dedicated_master_count   = "3"
    dedicated_master_enabled = "true"
    dedicated_master_type    = "m4.4xlarge.elasticsearch"
    instance_count           = "2"
  }

  advanced_options {
    "rest.action.multi.allow_explicit_index" = "true"
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp2"
    volume_size = 700
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
