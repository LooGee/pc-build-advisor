variable "aws_region" {
  default = "ap-northeast-2"
}

variable "environment" {
  default = "production"
}

variable "db_instance_class" {
  default = "db.t4g.medium"
}

variable "db_username" {
  sensitive = true
}

variable "db_password" {
  sensitive = true
}

variable "redis_node_type" {
  default = "cache.t4g.micro"
}

variable "ecr_registry" {
  description = "ECR registry URL"
}

variable "image_tag" {
  default = "latest"
}
