provider "aws" {
  region = "us-west-1"
}

data "aws_availability_zones" "available" {}

resource "aws_launch_configuration" "cccatalog-api-launch-config" {
  image_id        = "ami-00d8c660"
  instance_type   = "t2.micro"
  security_groups = ["${aws_security_group.cccatalog-sg.id}",
                     "${aws_security_group.cccatalog-api-ingress.id}"]

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "cccatalog-api-asg" {
  launch_configuration = "${aws_launch_configuration.cccatalog-api-launch-config.id}"
  min_size             = 2
  max_size             = 5
  availability_zones   = ["${data.aws_availability_zones.available.names}"]

  tag {
    key                 = "Name"
    value               = "cccatalog-api-autoscaling-group-dev"
    propagate_at_launch = true
  }

  tag {
    key                 = "Environment"
    value               = "dev"
    propagate_at_launch = true
  }
}

resource "aws_security_group" "cccatalog-api-ingress" {
  name = "cccatalog-api-ingress"

  # N California VPC "default"
  vpc_id = "vpc-d6b1bfb4"

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    # Only allow traffic from within the VPC, such as from the load balancer
    cidr_blocks = ["172.31.0.0/16"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "cccatalog-sg" {
  name   = "cccatalog-security-group"
  vpc_id = "vpc-d6b1bfb4"

  lifecycle {
    create_before_destroy = true
  }
}

# Public-facing load balancer
resource "aws_alb" "cccatalog-api-load-balancer" {
  name                       = "cccatalog-api-alb"
  internal                   = false
  load_balancer_type         = "application"
  security_groups            = ["${aws_security_group.cccatalog-sg.id}"]
  enable_deletion_protection = false
  subnets                    = ["subnet-05bfb167", "subnet-aa2369ec"]

  tags {
    Name        = "cccatalog-api-load-balancer-dev"
    Environment = "dev"
  }
}

resource "aws_alb_target_group" "ccc-api-asg-target" {
  name     = "ccc-api-autoscale-target"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = "vpc-d6b1bfb4"
}

resource "aws_alb_listener" "ccc-api-asg-listener" {
  load_balancer_arn = "${aws_alb.cccatalog-api-load-balancer.id}"
  port              = 80
  protocol          = "HTTP"

  default_action {
    target_group_arn = "${aws_alb_target_group.ccc-api-asg-target.id}"
    type             = "forward"
  }
}

resource "aws_security_group" "cccatalog-alb-sg" {
  name   = "cccatalog-alb-sg"
  vpc_id = "vpc-d6b1bfb4"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name = "cccatalog-alb-sg"
  }
}
