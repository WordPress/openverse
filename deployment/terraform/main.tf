provider "aws" {
  region = "us-west-1"
}

resource "aws_instance" "cccatalog-api-server" {
  # Amazon Linux 2 LTS Candidate 2
  ami           = "ami-00d8c660"
  instance_type = "t2.micro"

  tags {
    Name = "cccatalog-api-terraformtest"
    system = "cccatalog-backend"
    Environment = "dev"
  }

  vpc_security_group_ids = ["${aws_security_group.cccatalog-api-ingress.id}",
                            "${aws_security_group.cccatalog-sg.id}"
  ]
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "cccatalog-api-ingress" {
  name = "cccatalog-api-ingress"

  # N California VPC "default"
  vpc_id = "vpc-d6b1bfb4"

  ingress {
    from_port = 8080
    to_port = 8080
    protocol = "tcp"
    # Only allow traffic from within the VPC, such as from the load balancer
    cidr_blocks = ["172.31.0.0/16"]
  }

  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_security_group" "cccatalog-sg" {
  name = "cccatalog-security-group"
  vpc_id = "vpc-d6b1bfb4"

  lifecycle {
    create_before_destroy = true
  }
}

# Public-facing load balancer
resource "aws_lb" "cccatalog-api-load-balancer" {
  name = "cccatalog-api-lb"
  internal = false
  load_balancer_type = "application"
  security_groups = ["${aws_security_group.cccatalog-sg.id}"]
  enable_deletion_protection = false

  tags {
    Environment = "dev"
  }
}

resource "aws_security_group" "cccatalog-lb-ingress" {
  name = "cccatalog-lb-ingress"
  vpc_id = "vpc-d6b1bfb4"

  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
