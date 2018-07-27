# A templated bash script that bootstraps the docker daemon and runs a container.
data "template_file" "init"{
  template = "${file("${path.module}/init.tpl")}"

  # Templated variables passed to initialization script.
  vars {
    redis_password = "${var.redis_password}"
  }
}

# VPC subnets
data "aws_subnet_ids" "subnets" {
  vpc_id = "${var.vpc_id}"
}

resource "aws_security_group" "cacheserver-sg" {
  name_prefix = "cacheserver-sg-${var.environment}"
  vpc_id = "${var.vpc_id}"

  # Allow incoming SSH from the internet
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow Redis ingress from within the us-east-1 VPC.
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["172.30.0.0/16"]
  }

  # Unrestricted egress
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "cacheserver-ec2" {
  ami                    = "ami-b70554c8"
  instance_type          = "${var.instance_type}"
  user_data              = "${data.template_file.init.rendered}"
  # Launch it on the first available subnet
  subnet_id              = "${element(data.aws_subnet_ids.subnets.ids, 0)}"
  key_name               = "cccapi-admin"
  vpc_security_group_ids = ["${aws_security_group.cacheserver-sg.id}"]

  tags {
    Name        = "cacheserver-${var.environment}"
    environment = "${var.environment}"
  }
}
