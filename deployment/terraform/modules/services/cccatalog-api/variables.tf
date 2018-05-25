variable "environment" {
  description = "The staging environment of a deployment, typically 'dev' or 'prod'."
}

variable "min_size" {
  description = "The minimum number of API server autoscaled instances."
  default     = 1
}

variable "max_size" {
  description = "The maximum number of API server autoscaled instances."
  default     = 5
}

variable "instance_type" {
  description = "The EC2 instance type of API server autoscaled instances."
  default     = "t2.micro"
}

variable "enable_monitoring" {
  description = "Whether CloudWatch is enabled for the API server autoscaling launch configuration."
  default     = "false"
}
