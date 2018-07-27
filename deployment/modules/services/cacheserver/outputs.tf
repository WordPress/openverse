output "ec2-instance-url" {
  value = "${aws_instance.cacheserver-ec2.public_dns}"
}