
resource "aws_security_group" "ecs_tasks" {
  name        = "skystock-dev-ecs-sg"
  description = "Security group for SkyStock ECS tasks"
  vpc_id      = aws_vpc.skystock.id

  tags = {
    Name = "skystock-dev-ecs-sg"
  }
}

resource "aws_security_group" "database" {
  name        = "skystock-dev-db-sg"
  description = "Security group for SkyStock PostgreSQL"
  vpc_id      = aws_vpc.skystock.id

  tags = {
    Name = "skystock-dev-db-sg"
  }
}

resource "aws_vpc_security_group_egress_rule" "ecs_outbound" {
  security_group_id = aws_security_group.ecs_tasks.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
  description       = "Allow ECS outbound connections"
}

resource "aws_vpc_security_group_ingress_rule" "db_from_ecs" {
  security_group_id            = aws_security_group.database.id
  referenced_security_group_id = aws_security_group.ecs_tasks.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  description                  = "PostgreSQL access from ECS only"
}
