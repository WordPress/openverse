# An SSL proxy for accessing backend monitoring tools hosted in us-east-1, such as Graylog and Kibana.

variable "cloudflare_email" {}
variable "cloudflare_token" {}

provider "cloudflare" {
  email = "${var.cloudflare_email}"
  token = "${var.cloudflare_token}"
}

provider "aws" {
  region = "us-east-1"
}

# Public URL for accessing SSL proxy
resource "cloudflare_record" "graylog-cc-engineering" {
  domain = "creativecommons.engineering"
  name   = "graylog"
  value  = "${aws_instance.ssl-gateway.public_ip}"
  type   = "A"
  ttl    = 120
}


data "aws_subnet_ids" "subnets" {
  vpc_id = "vpc-b741b4cc"
}
# Web server AMI
data "aws_ami" "amazon_linux_2" {
    most_recent = true

    filter {
        name   = "name"
        values = ["amzn2-ami-hvm-2.0.*x86_64-gp2"]
    }

    filter {
        name   = "virtualization-type"
        values = ["hvm"]
    }

    owners = ["137112412989"] # Amazon
}

# Templated bash script for bootstrapping SSL gateway
data "template_file" "gateway-init" {
  template = "${file("${path.module}/proxy-init.tpl")}"
}

resource "aws_security_group" "ssl-gateway-sg" {
  name = "ssl-gateway-sg"
  vpc_id = "vpc-b741b4cc"

  # Allow incoming SSL traffic from the internet
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    cidr_blocks     = ["0.0.0.0/0"]
  }
  # Allow incoming HTTP traffic from the internet (required by certbot)
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    cidr_blocks     = ["0.0.0.0/0"]
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

resource "aws_instance" "ssl-gateway" {
  ami                    = "${data.aws_ami.amazon_linux_2.id}"
  instance_type          = "t2.micro"
  user_data              = "${data.template_file.gateway-init.rendered}"
  # Launch it on the first available subnet
  subnet_id              = "${element(data.aws_subnet_ids.subnets.ids, 0)}"
  key_name               = "cccapi-admin"
  vpc_security_group_ids = ["${aws_security_group.ssl-gateway-sg.id}"]

  tags {
    Name        = "ssl-gateway"
    environment = "prod"
  }
}

