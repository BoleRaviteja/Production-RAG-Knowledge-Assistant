resource "random_password" "jwt" {
  length  = 64
  special = false
}

resource "aws_secretsmanager_secret" "app" {
  name                    = "${local.name}/app"
  description             = "Runtime secrets injected into the Helm release by CI"
  recovery_window_in_days = 0 # allows quick re-create in dev; use 7-30 for real prod
}

# NOTE: values land in Terraform state - keep state encrypted (S3 backend + KMS).
resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    DATABASE_URL      = "postgresql+psycopg://${aws_db_instance.this.username}:${random_password.db.result}@${aws_db_instance.this.address}:5432/${aws_db_instance.this.db_name}?sslmode=require"
    JWT_SECRET        = random_password.jwt.result
    ANTHROPIC_API_KEY = var.anthropic_api_key
    OPENAI_API_KEY    = var.openai_api_key
  })
}
