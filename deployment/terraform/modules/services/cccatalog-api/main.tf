# List of availability zones
data "aws_availability_zones" "available" {}

# A templated bash script file that bootstraps the API server. 
data "template_file" "init"{
  template = "${file("${path.module}/init.tpl")}"

  # Pass environment variables to the server
  vars {
    database_host        = "${var.database_host}"
    database_password    = "${var.database_password}"
    django_debug_enabled = "${var.django_debug_enabled}"
    django_secret_key    = "${var.django_secret_key}"
    git_revision         = "${var.git_revision}}"
  }
}

# API server autoscaling launch configuration
resource "aws_launch_configuration" "cccatalog-api-launch-config" {
  name_prefix              = "cccatalog-api-asg-${var.environment}"
  image_id                 = "ami-00d8c660"
  instance_type            = "${var.instance_type}"
  security_groups          = ["${aws_security_group.cccatalog-sg.id}",
                              "${aws_security_group.cccatalog-api-ingress.id}"]
  enable_monitoring        = "${var.enable_monitoring}"
  key_name                 = "${aws_key_pair.cccapi-admin.key_name}"
  user_data                = "${data.template_file.init.rendered}"

  lifecycle {
    create_before_destroy  = true
  }
}

# API server autoscaling group
# Changes to the launch configuration result in automated zero-downtime redeployment
resource "aws_autoscaling_group" "cccatalog-api-asg" {
  name                 = "${aws_launch_configuration.cccatalog-api-launch-config.id}"
  launch_configuration = "${aws_launch_configuration.cccatalog-api-launch-config.id}"
  min_size             = "${var.min_size}"
  max_size             = "${var.max_size}"
  min_elb_capacity     = "${var.min_size}"
  availability_zones   = ["${data.aws_availability_zones.available.names}"]
  target_group_arns    = ["${aws_alb_target_group.ccc-api-asg-target.id}"]

  tag {
    key                 = "Name"
    value               = "cccatalog-api-autoscaling-group-${var.environment}"
    propagate_at_launch = true
  }

  tag {
    key                 = "Environment"
    value               = "${var.environment}"
    propagate_at_launch = true
  }

  tag {
    key                 = "service"
    value               = "cccatalog-api-django"
    propagate_at_launch = true
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_key_pair" "cccapi-admin" {
  key_name   = "cccapi-admin"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCzocO5AKxkGVTtpmtgVd0UrpI2//v6YO8kxKZQ5t99sK0K62QG1PQj+nxFA5wCkiGNJohlvVX+Hl1ZujDLH3/G9yPaUbOA4MeDEUy3JQSxTfMVcPKVTocAldU5A/5LkxIsB+XwDY/JFr7aQq3YlwLikJ2Sb6LFaUACJWzXKMa2zTE7TvHYpJqB4UihAFVuuqQPBH5PzwXjeHJcq/zIZgnB9orMfK0Fci5YRp2wdY/RWqJwDAuTpfvaGCZmghqo0ogAmm+Dz0EPGu9jJrRvlZ7c0c1bP+eWTuHIeiXsuAN6wlkXuu8hRXRwbBdVox7ST8x8eRBUdWZZcaoeZ69dI2HZ webmaster@creativecommons.org"
}

resource "aws_security_group" "cccatalog-api-ingress" {
  name = "cccatalog-api-ingress"

  # N California VPC "default"
  vpc_id = "vpc-d6b1bfb4"

  # Allow incoming traffic from the load balancer and autoscale clones
  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = ["${aws_security_group.cccatalog-alb-sg.id}"]
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
  security_groups            = ["${aws_security_group.cccatalog-sg.id}",
                                "${aws_security_group.cccatalog-alb-sg.id}"]
  enable_deletion_protection = false
  subnets                    = ["subnet-05bfb167", "subnet-aa2369ec"]

  tags {
    Name        = "cccatalog-api-load-balancer-${var.environment}"
    Environment = "${var.environment}"
  }
}

resource "aws_alb_target_group" "ccc-api-asg-target" {
  name     = "ccc-api-autoscale-target"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = "vpc-d6b1bfb4"

  health_check {
    path = "/healthcheck"
    port = 8080
    
  }
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
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name = "cccatalog-alb-sg"
  }
}
