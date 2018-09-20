# VPC subnets
data "aws_subnet_ids" "subnets" {
  vpc_id = "${var.vpc_id}"
}

# Start script
data "template_file" "init" {
  template = "${file("${path.module}/init.tpl")}"

  # Pass configuration variables to the script
  vars {
    git_revision = "${var.git_revision}"
    api_url      = "${var.api_url}"
  }
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


# API server autoscaling launch configuration
resource "aws_launch_configuration" "ccsearch-launch-config" {
  name_prefix              = "ccsearch-asg${var.environment}"
  image_id                 = "${data.aws_ami.amazon_linux_2.id}"
  instance_type            = "${var.instance_type}"
  security_groups          = ["${aws_security_group.ccsearch-sg.id}",
                              "${aws_security_group.ccsearch-ingress.id}"]
  enable_monitoring        = false
  key_name                 = "cccapi-admin"
  user_data                = "${data.template_file.init.rendered}"

  lifecycle {
    create_before_destroy  = true
  }
}

# API server autoscaling group
# Changes to the launch configuration result in automated zero-downtime redeployment
resource "aws_autoscaling_group" "ccsearch-asg" {
  name                 = "${aws_launch_configuration.ccsearch-launch-config.id}"
  launch_configuration = "${aws_launch_configuration.ccsearch-launch-config.id}"
  min_size             = "3"
  max_size             = "3"
  min_elb_capacity     = "1"
  vpc_zone_identifier  = ["${data.aws_subnet_ids.subnets.ids}"]
  target_group_arns    = ["${aws_alb_target_group.ccsearch-asg-target.id}"]
  wait_for_capacity_timeout = "8m"

  tag {
    key                 = "Name"
    value               = "ccsearch-autoscaling-group${var.environment}"
    propagate_at_launch = true
  }

  tag {
    key                 = "Environment"
    value               = "${var.environment}"
    propagate_at_launch = true
  }

  tag {
    key                 = "service"
    value               = "ccsearch-django"
    propagate_at_launch = true
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "ccsearch-ingress" {
  name = "ccsearch-ingress${var.environment}"
  vpc_id = "${var.vpc_id}"

  # Allow incoming traffic from the load balancer and autoscale clones
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = ["${aws_security_group.ccsearch-alb-sg.id}"]
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

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "ccsearch-sg" {
  name   = "ccsearch-security-group${var.environment}"
  vpc_id = "${var.vpc_id}"


  lifecycle {
    create_before_destroy = true
  }
}

# Public-facing load balancer
resource "aws_alb" "ccsearch-load-balancer" {
  name                       = "ccsearch-alb${var.environment}"
  internal                   = false
  load_balancer_type         = "application"
  security_groups            = ["${aws_security_group.ccsearch-sg.id}",
                                "${aws_security_group.ccsearch-alb-sg.id}"]
  enable_deletion_protection = false
  subnets                    = ["${data.aws_subnet_ids.subnets.ids}"]

  tags {
    Name        = "ccsearch-load-balancer${var.environment}"
    Environment = "${var.environment}"
  }
}

resource "aws_alb_target_group" "ccsearch-asg-target" {
  name     = "ccsearch-autoscale-target${var.environment}"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = "${var.vpc_id}"


  health_check {
    path = "/healthcheck"
    port = 8080
  }
}

resource "aws_alb_listener" "ccsearch-asg-listener" {
  load_balancer_arn = "${aws_alb.ccsearch-load-balancer.id}"
  port              = 80
  protocol          = "HTTP"

  default_action {
    type          = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_alb_listener" "ccsearch-asg-listener-ssl" {
  load_balancer_arn = "${aws_alb.ccsearch-load-balancer.id}"
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = "arn:aws:acm:us-east-1:664890800379:certificate/a873ac2b-3aae-43be-a810-678de291d6cd"

  default_action {
    target_group_arn = "${aws_alb_target_group.ccsearch-asg-target.id}"
    type             = "forward"
  }
}

resource "aws_security_group" "ccsearch-alb-sg" {
  name   = "ccsearch-alb-sg${var.environment}"
  vpc_id = "${var.vpc_id}"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name = "ccsearch-alb-sg"
  }
}
