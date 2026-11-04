
resource "aws_ecs_service" "skystock" {
  name            = "skystock-dev-service"
  cluster         = aws_ecs_cluster.skystock.id
  task_definition = aws_ecs_task_definition.skystock.arn

  launch_type      = "FARGATE"
  platform_version = "LATEST"

  # Keep containers stopped until testing
  desired_count = 0

  network_configuration {
    subnets = aws_subnet.public[*].id

    security_groups = [
      aws_security_group.ecs_tasks.id
    ]

    assign_public_ip = true
  }

  tags = {
    Name = "skystock-dev-service"
  }
}
