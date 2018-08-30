variable "instance_type" {
  description = "The EC2 instance type that the frontend will be deployed to."
  default = "t2.medium"
}

variable "vpc_id" {
  description = "The VPC to host the frontend on."
}

variable "environment" {
  description = "The name of the deployment environment (such as 'dev')"
}

variable "git_revision"{
  description = "The git commit hash to deploy."
}
