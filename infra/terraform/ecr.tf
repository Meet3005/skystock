
resource "aws_ecr_repository" "api" {
  name                 = "skystock-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "skystock-api"
  }
}

resource "aws_ecr_repository" "frontend" {
  name                 = "skystock-frontend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "skystock-frontend"
  }
}
