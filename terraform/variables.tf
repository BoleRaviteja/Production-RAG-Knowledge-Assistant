variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "project" {
  type    = string
  default = "rag-assistant"
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "github_repo" {
  description = "GitHub repo allowed to deploy, e.g. my-org/rag-assistant"
  type        = string
}

variable "create_github_oidc_provider" {
  description = "Set false if the account already has the GitHub OIDC provider"
  type        = bool
  default     = true
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "az_count" {
  type    = number
  default = 2
}

variable "single_nat_gateway" {
  description = "true = cheaper (1 NAT); false = one NAT per AZ for HA"
  type        = bool
  default     = true
}

variable "eks_version" {
  type    = string
  default = "1.31"
}

variable "node_instance_types" {
  type    = list(string)
  default = ["t3.large"]
}

variable "node_min_size" {
  type    = number
  default = 2
}

variable "node_max_size" {
  type    = number
  default = 4
}

variable "node_desired_size" {
  type    = number
  default = 2
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.medium"
}

variable "db_allocated_storage" {
  type    = number
  default = 20
}

variable "db_multi_az" {
  type    = bool
  default = false
}

variable "db_deletion_protection" {
  description = "Set true for real production data"
  type        = bool
  default     = false
}

variable "alert_email" {
  description = "Email for CloudWatch alarm notifications (empty = no subscription)"
  type        = string
  default     = ""
}

variable "anthropic_api_key" {
  type      = string
  default   = ""
  sensitive = true
}

variable "openai_api_key" {
  type      = string
  default   = ""
  sensitive = true
}
