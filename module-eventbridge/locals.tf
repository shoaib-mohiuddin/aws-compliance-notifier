locals {
  enabled_checks = compact([
    var.enable_gp2_check         ? "ebs_gp2"         : "",
    var.enable_encryption_check ? "ebs_unencrypted" : "",
    var.enable_sg_check          ? "security_groups" : ""
  ])
  exclusions = {
    ebs_gp2_volume_ids         = var.exclude_gp2_volumes
    ebs_unencrypted_volume_ids = var.exclude_unencrypted_volumes
    security_group_rule_ids    = var.exclude_sg_rules
  }
}
