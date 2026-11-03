
resource "aws_db_subnet_group" "skystock" {
  name        = "skystock-dev-db-subnets"
  description = "Private database subnets for SkyStock"

  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "skystock-dev-db-subnets"
  }
}


resource "aws_db_instance" "skystock" {
  identifier = "skystock-dev-postgres"

  engine         = "postgres"
  engine_version = "17"
  instance_class = "db.t4g.micro"

  allocated_storage = 20
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = "skystock"
  username = "skystock_admin"

  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.skystock.name
  vpc_security_group_ids = [aws_security_group.database.id]

  publicly_accessible = false
  multi_az            = false

  backup_retention_period = 1

  deletion_protection = false
  skip_final_snapshot = true

  tags = {
    Name = "skystock-dev-postgres"
  }
}
