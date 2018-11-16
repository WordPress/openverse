# The development database is in a different region than the rest of the infrastructure in order to make use of
# Amazon Glue and other AWS analytics services not yet rolled out to us-west-1.
provider "aws" {
  region = "us-east-1"
}

# Secrets must be passed in externally
variable "database_password" {
  type = "string"
}

resource "aws_db_instance" "cccatalog-postgres-prod" {
  instance_class             = "db.m4.4xlarge"
  engine                     = "postgres"
  engine_version             = "10.3"
  port                       = 5432
  name                       = "openledger"
  username                   = "deploy"
  password                   = "${var.database_password}"
  publicly_accessible        = false
  vpc_security_group_ids     = ["sg-1fea4057", "sg-3778d37f"]
  apply_immediately          = false
  backup_retention_period    = 7 # days
  backup_window              = "07:16-07:46" # utc time
  auto_minor_version_upgrade = true
  storage_encrypted          = false
  db_subnet_group_name       = "default-vpc-b741b4cc"
  parameter_group_name       = "default.postgres10"
  snapshot_identifier        = "prod-snapshot-pre-200mm-migration"
  
  tags = {
    name  = "Name"
    value = "production-api-200mm"
  }
}
