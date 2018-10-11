# Resources required to run Graylog. Includes a single EC2 instance and an
# inexpensive Elasticsearch instance. Cloudflare handles the DNS.

# Pass in sensitive data through tfvars.
variable "cloudflare_email" {}
variable "cloudflare_token" {}
variable "graylog_password" {}
variable "graylog_sha2" {}

# List of available subnets
data "aws_subnet_ids" "subnets" {
  vpc_id = "vpc-b741b4cc"
}

provider "cloudflare" {
  email = "${var.cloudflare_email}"
  token = "${var.cloudflare_token}"
}

provider "aws" {
  region = "us-east-1"
}

data "template_file" "graylog-init"{
  template = "${file("${path.module}/init.tpl")}"

  # Templated variables passed to initialization script.
  vars {
    graylog_password   = "${var.graylog_password}"
    graylog_sha2       = "${var.graylog_sha2}"
    elasticsearch_host = "${aws_elasticsearch_domain.graylog-es-backend.endpoint}"
  }
}

resource "aws_security_group" "graylog-frontend-sg" {
  name = "graylog-frontend-sg"
  vpc_id = "vpc-b741b4cc"

  # Allow incoming traffic from the internet to reach password-secured graylog.
  ingress {
    from_port       = 9000
    to_port         = 9000
    protocol        = "tcp"
    cidr_blocks     = ["0.0.0.0/0"]
  }

  # Allow incoming messages only from traffic internal to the VPC.
  ingress {
    from_port       = 12201
    to_port         = 12201
    protocol        = "tcp"
    cidr_blocks     =  ["172.31.0.0/16"]
  }

  # Allow filebeat traffic internally
  ingress {
    from_port       = 5044
    to_port         = 5044
    protocol        = "tcp"
    cidr_blocks     = ["172.31.0.0/16"]
  }

   # Allow internal VPC traffic access to rsyslog port
  ingress {
    from_port       = 514
    to_port         = 514
    protocol        = "tcp"
    cidr_blocks     =  ["172.31.0.0/16"]
  }


  # Allow incoming SSH from the internet
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Unrestricted egress
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "graylog-frontend" {
  ami                    = "ami-b70554c8"
  instance_type          = "t2.medium"
  user_data              = "${data.template_file.graylog-init.rendered}"
  subnet_id              = "${element(data.aws_subnet_ids.subnets.ids, 0)}"
  key_name               = "cccapi-admin"
  vpc_security_group_ids = ["${aws_security_group.graylog-frontend-sg.id}"]
  tags {
    Name = "graylog-prod"
    environment = "prod"
  }
}

resource "cloudflare_record" "graylog-cc-engineering" {
  domain = "creativecommons.engineering"
  name   = "graylog"
  value  = "${aws_instance.graylog-frontend.public_ip}"
  type   = "A"
  ttl    = 120
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
          "aws:SourceIp": "34.224.64.90/32"
        }
      }
    }
  ]
}
EOF
}
