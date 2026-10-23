terraform {
  required_version = ">= 1.6"

  required_providers {
    aws        = { source = "hashicorp/aws", version = "~> 5.60" }
    random     = { source = "hashicorp/random", version = "~> 3.6" }
    helm       = { source = "hashicorp/helm", version = "~> 2.13" }
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.30" }
  }

  # Recommended for teams: remote state. Create the bucket + lock table first.
  # backend "s3" {
  #   bucket         = "my-tf-state-bucket"
  #   key            = "rag-assistant/prod.tfstate"
  #   region         = "ap-south-1"
  #   dynamodb_table = "tf-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.region
  default_tags { tags = local.tags }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name, "--region", var.region]
    }
  }
}
