provider "aws" {
  region = "us-east-1"
}

# ECR Repository for Docker images
resource "aws_ecr_repository" "legal_ai_classifier_repo" {
  name                 = "legal-ai-classifier"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# AWS App Runner Service (Simpler alternative to ECS for fast container deployment)
resource "aws_apprunner_service" "legal_ai_classifier_service" {
  service_name = "legal-ai-classifier-service"

  source_configuration {
    image_repository {
      image_configuration {
        port = "8000"
      }
      image_identifier      = "${aws_ecr_repository.legal_ai_classifier_repo.repository_url}:latest"
      image_repository_type = "ECR"
    }
    auto_deployments_enabled = true
  }

  instance_configuration {
    cpu    = "1024"
    memory = "2048"
  }

  tags = {
    Environment = "Production"
    Project     = "Legal-AI-Classifier"
  }
}

output "apprunner_service_url" {
  value = aws_apprunner_service.legal_ai_classifier_service.service_url
}