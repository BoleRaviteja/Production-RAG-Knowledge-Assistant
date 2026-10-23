resource "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_security_group" "rds" {
  name_prefix = "${local.name}-rds-"
  description = "Postgres access from EKS nodes only"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "Postgres from EKS nodes"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  lifecycle { create_before_destroy = true }
}

resource "aws_db_instance" "this" {
  identifier     = local.name
  engine         = "postgres"
  engine_version = "16" # pgvector is available on RDS PostgreSQL 15.2+ / 16.x
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_allocated_storage * 5
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "rag"
  username = "rag_admin"
  password = random_password.db.result

  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  multi_az               = var.db_multi_az

  backup_retention_period         = 7
  deletion_protection             = var.db_deletion_protection
  skip_final_snapshot             = !var.db_deletion_protection
  final_snapshot_identifier       = var.db_deletion_protection ? "${local.name}-final" : null
  performance_insights_enabled    = true
  enabled_cloudwatch_logs_exports = ["postgresql"]
  auto_minor_version_upgrade      = true
  apply_immediately               = true
}
