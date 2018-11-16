provider "aws" {
  region = "us-east-1"
}

resource "aws_elasticsearch_domain" "graylog-es-backend" {
  domain_name           = "graylog-es-backend"
  # Graylog doesn't support v6.x yet
  elasticsearch_version = "5.6"
  cluster_config {
    instance_type            = "m4.large.elasticsearch"
    dedicated_master_enabled = "false"
    instance_count           = "1"
  }

  advanced_options {
    "rest.action.multi.allow_explicit_index" = "true"
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp2"
    volume_size = 500
  }

  # Note that the access policy IP whitelist is updated automatically by Graylog upon deployment.
  # Applying this Terraform file without first updating the policy will wipe out the whitelist
  access_policies =<<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::664890800379:user/openledger"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:664890800379:domain/graylog-es-backend/*"
    },
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:664890800379:domain/graylog-es-backend/*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "54.225.52.99/32"
        }
      }
    }
  ]
}
EOF
}
