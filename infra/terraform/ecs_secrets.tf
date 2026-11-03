
# Allow ECS to retrieve the RDS master password
# from AWS Secrets Manager.

data "aws_iam_policy_document" "ecs_rds_secret" {
  statement {
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue"
    ]

    resources = [
      aws_db_instance.skystock.master_user_secret[0].secret_arn
    ]
  }
}

resource "aws_iam_role_policy" "ecs_rds_secret" {
  name = "skystock-ecs-rds-secret"
  role = aws_iam_role.ecs_execution.id

  policy = data.aws_iam_policy_document.ecs_rds_secret.json
}
