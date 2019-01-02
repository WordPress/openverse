output "ec2-instance-url" {
  value = "${aws_instance.ingestion-server-ec2.public_dns}"
}