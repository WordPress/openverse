variable "aws_access_key_id" {
  description = "The access key ID used to connect to Elasticsearch."
}

variable "aws_secret_access_key" {
  description = "The secret access key used to connect to Elasticsearch."
}

variable "elasticsearch_url" {
  description = "The URL of the Elasticsearch instance to synchronize."
}

variable "elasticsearch_port" {
  description = "The port used to connect to Elasticsearch."
}

variable "aws_region" {
  description = "The region of the Elasticsearch instance. Required for IAM auth."
}

variable "database_host" {
  description = "Postgres URL"
}

variable "database_password" {
  description = "Postgres password"
}

variable "database_port" {
  description = "Postgres port"
}

variable "db_buffer_size" {
  description = "The number of database records to store in memory at once. This should be tuned to use as much available memory as possible."
  default = "100000"
}

variable "copy_tables" {
  description = "A comma-separated list of tables to replicate to Elasticsearch. (ex: image,doc)"
  default = "image"
}

variable "instance_type" {
  description = "The EC2 instance type that the synchronizer will be deployed to."
  default = "t2.medium"
}

variable "vpc_id" {
  description = "The VPC to host the synchronizer on."
}

variable "environment" {
  description = "The name of the deployment environment (such as 'dev')"
}