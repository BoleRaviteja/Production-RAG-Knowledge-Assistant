output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "cluster_name" {
  value = module.eks.cluster_name
}

output "kubeconfig_command" {
  value = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.region}"
}

output "rds_endpoint" {
  value = aws_db_instance.this.address
}

output "app_secret_id" {
  value = aws_secretsmanager_secret.app.name
}

output "github_deploy_role_arn" {
  description = "Put this in the GitHub secret AWS_DEPLOY_ROLE_ARN"
  value       = aws_iam_role.github_deploy.arn
}
