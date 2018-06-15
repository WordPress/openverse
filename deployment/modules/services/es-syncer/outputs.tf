output "ec2-instance-url" {
  value = "${aws_instance.es-syncer-ec2.public_dns}"
}