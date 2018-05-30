output "load-balancer-url" {
  value = "${module.cccatalog-api.load-balancer-url}"
}

output "autoscaling-group-name" {
  value = "${module.cccatalog-api.autoscaling-group-name}"
}
