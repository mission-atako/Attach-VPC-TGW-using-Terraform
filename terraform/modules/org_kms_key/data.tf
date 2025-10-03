data "aws_organizations_organization" "org" {}
data "aws_caller_identity" "this" {}

data "aws_iam_policy_document" "key" {
  statement {
    sid = "AllowAdmin"
    actions = [
      "kms:*"
    ]
    resources = ["*"]
    principals {
      identifiers = [
        "arn:aws:iam::${data.aws_caller_identity.this.id}:root",
        "arn:aws:iam::${data.aws_caller_identity.this.id}:role/aws-reserved/sso.amazonaws.com/us-west-2/AWSReservedSSO_AdministratorAccess_4df11490af948be6",
        "arn:aws:iam::${data.aws_caller_identity.this.id}:role/MissionProfessionalServicesEngineer"
      ]
      type = "AWS"
    }
  }
  statement {
    sid = "BackupVaultKeyPolicy"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = ["*"]
    principals {
      identifiers = [var.aws_service]
      type        = "Service"
    }
  }
  statement {
    sid = "BackupVaultKeyPolicyOrg"
    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:GenerateDataKey*",
      "kms:Encrypt",
      "kms:ReEncrypt*",
      "kms:GetKeyPolicy",
      "kms:CreateGrant",
      "kms:ListGrants",
      "kms:ListAliases",
      "kms:RevokeGrant"
    ]
    resources = ["*"]
    principals {
      identifiers = ["*"]
      type        = "AWS"
    }
    condition {
      test     = "StringEquals"
      variable = "aws:PrincipalOrgID"
      values   = [data.aws_organizations_organization.org.id]
    }
  }
}