resource "aws_kms_key" "this" {
  description             = "Multi Region Key for ${var.aws_service}"
  multi_region            = true
  enable_key_rotation     = true
  deletion_window_in_days = var.deletion_window_in_days
}

resource "aws_kms_key_policy" "this" {
  key_id = aws_kms_key.this.id
  policy = data.aws_iam_policy_document.key.json
}

resource "aws_kms_alias" "this" {
  count         = var.alias == "" ? 0 : 1
  target_key_id = aws_kms_key.this.key_id
  name          = var.alias
}

resource "aws_kms_replica_key" "replica" {
  for_each                = { for k in var.replica_regions : k => k }
  description             = "replica key for ${var.aws_service}"
  deletion_window_in_days = var.deletion_window_in_days
  primary_key_arn         = aws_kms_key.this.arn
  region                  = each.value
}

resource "aws_kms_key_policy" "replica" {
  for_each = { for k in var.replica_regions : k => k }
  region   = each.value
  key_id   = aws_kms_replica_key.replica[each.key].key_id
  policy   = data.aws_iam_policy_document.key.json
}

resource "aws_kms_alias" "replica" {
  for_each      = var.alias == "" ? {} : { for k in var.replica_regions : k => k }
  region        = each.value
  target_key_id = aws_kms_replica_key.replica[each.value].key_id
  name          = "${var.alias}-${each.value}"
}