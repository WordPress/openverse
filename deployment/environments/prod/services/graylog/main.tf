# Resources required to run Graylog. Includes a single EC2 instance and an
# inexpensive Elasticsearch instance. Cloudflare handles the DNS.

provider "aws" {
  region = "us-east-1"
}

# Pass in sensitive data through tfvars.
variable "graylog_password" {}
variable "graylog_sha2" {}

# List of available subnets
data "aws_subnet_ids" "subnets" {
  vpc_id = "vpc-b741b4cc"
}

# Internal URL for submitting logs to Graylog
resource "aws_route53_zone" "graylog-private-dns" {
  name = "graylog.private"
  vpc_id = "vpc-b741b4cc"
}

resource "aws_route53_record" "graylog-private-a-record" {
  name    = "graylog.private"
  type    = "A"
  ttl     = 120
  records = ["${aws_instance.graylog-frontend.private_ip}"]
  zone_id = "${aws_route53_zone.graylog-private-dns.id}"
}

data "template_file" "graylog-init"{
  template = "${file("${path.module}/init.tpl")}"

  # Templated variables passed to initialization script.
  vars {
    graylog_password   = "${var.graylog_password}"
    graylog_sha2       = "${var.graylog_sha2}"
    elasticsearch_host = "search-graylog-es-backend-jaives6z7cqeab56nds2u6kfoa.us-east-1.es.amazonaws.com"
  }
}

resource "aws_security_group" "graylog-frontend-sg" {
  name = "graylog-frontend-sg"
  vpc_id = "vpc-b741b4cc"

  # Allow incoming messages only from traffic internal to the VPC.
  ingress {
    from_port       = 12201
    to_port         = 12201
    protocol        = "tcp"
    cidr_blocks     =  ["172.30.0.0/16"]
  }

  # Allow filebeat traffic internally
  ingress {
    from_port       = 5044
    to_port         = 5044
    protocol        = "tcp"
    cidr_blocks     = ["172.30.0.0/16"]
  }

   # Allow internal VPC traffic access to rsyslog port
  ingress {
    from_port       = 514
    to_port         = 514
    protocol        = "tcp"
    cidr_blocks     =  ["172.30.0.0/16"]
  }

  # Allow incoming SSH from the internet
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Only allow access to the web dashboard via proxy.
  ingress {
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["172.30.0.0/16"]
  }

  # Allow incoming HTTPS from the internet
  ingress {
    from_port   = 443
    to_port     = 443
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

