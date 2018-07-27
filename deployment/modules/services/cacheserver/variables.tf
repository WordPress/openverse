variable redis_password {
  description = "Redis password"
}

variable environment {
  description = "The development environment (prod or dev)"
}

variable instance_type {
  description = "The EC2 instance type to deploy Redis to."
}

variable vpc_id {
  description = "The VPC to deploy to."
}