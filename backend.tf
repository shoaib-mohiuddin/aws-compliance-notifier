terraform {
  backend "s3" {
    bucket       = "talent-academy-lab-shoaib-tfstates-166916347510"
    key          = "talent-academy/aws-ebs-volume-audit/terraform.tfstates"
    region       = "eu-west-1"
    use_lockfile = true
  }
}