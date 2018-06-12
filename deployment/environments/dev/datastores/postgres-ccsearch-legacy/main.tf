# Database for the old ccsearch Django app
provider "aws" {
  region = "us-west-1"
}

# Secrets must be passed in externally
variable "database_password" {
  type = "string"
}

resource "aws_db_instance" "cccsearch-postgres-legacy" {
  identifier                 = "ccsearch-db-legacy-dev"
  instance_class             = "db.t2.small"
  engine                     = "postgres"
  engine_version             = "10.3"
  port                       = 5432
  name                       = "openledger"
  username                   = "deploy"
  password                   = "${var.database_password}"
  publicly_accessible        = false
  vpc_security_group_ids     = ["sg-2e7f764c"]
  apply_immediately          = false
  backup_retention_period    = 7 # days
  backup_window              = "07:16-07:46" # utc time
  auto_minor_version_upgrade = true
  storage_encrypted          = false
  db_subnet_group_name       = "default"
  parameter_group_name       = "default.postgres10"
  allocated_storage          = 100
  final_snapshot_identifier  = "deleteme"
}
