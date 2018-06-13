output "load-balancer-url" {
  value = "${aws_alb.cccatalog-api-load-balancer.dns_name}"
}

output "autoscaling-group-name" {
  value = "${aws_autoscaling_group.cccatalog-api-asg.name}"
}
