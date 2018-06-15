# A templated bash script that bootstraps the docker daemon and runs a container.
data "template_file" "init"{
  template = "${file("${path.module}/init.tpl")}"

  # Templated variables passed to initialization script.
  vars {
    aws_access_key_id     = "${var.aws_access_key_id}"
    aws_secret_access_key = "${var.aws_secret_access_key}"
    elasticsearch_url     = "${var.elasticsearch_url}"
    elasticsearch_port    = "${var.elasticsearch_port}"
    aws_region            = "${var.aws_region}"
    database_host         = "${var.database_host}"
    database_password     = "${var.database_password}"
    database_port         = "${var.database_port}"
    db_buffer_size        = "${var.db_buffer_size}"
    copy_tables           = "${var.copy_tables}"
  }
}

# VPC subnets
data "aws_subnet_ids" "subnets" {
  vpc_id = "${var.vpc_id}"
}

resource "aws_security_group" "es-syncer-sg" {
  name_prefix = "es-syncer-sg-${var.environment}"
  vpc_id = "${var.vpc_id}"

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

resource "aws_instance" "es-syncer-ec2" {
  ami                    = "ami-afd15ed0"
  instance_type          = "${var.instance_type}"
  user_data              = "${data.template_file.init.rendered}"
  # Launch it on the first available subnet
  subnet_id              = "${element(data.aws_subnet_ids.subnets.ids, 0)}"
  key_name               = "cccapi-admin"
  vpc_security_group_ids = ["${aws_security_group.es-syncer-sg.id}"]

  tags {
    Name        = "elastic-syncer-${var.environment}"
    environment = "${var.environment}"
  }
}