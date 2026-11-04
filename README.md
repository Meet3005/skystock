
# SkyStock | Cloud-Native Inventory Management Platform

A full-stack inventory management application built with React, Flask, and PostgreSQL, containerized with Docker and deployed on AWS using Terraform.

SkyStock demonstrates the design, deployment, and troubleshooting of a cloud-hosted application, from frontend development and REST APIs to database integration and infrastructure automation.

## Overview

SkyStock provides a centralized dashboard for managing product inventory, tracking stock changes, and monitoring inventory value.

The project focuses on building an application that works across multiple services while maintaining reliable data persistence and a reproducible cloud deployment process.

## Features

- Inventory dashboard with product counts, stock levels, and total inventory value
- Product creation with input validation
- Stock adjustments with transaction history
- Inventory valuation and low-stock monitoring
- REST API for inventory operations
- Persistent PostgreSQL storage
- Containerized frontend and backend
- Infrastructure provisioning through Terraform

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React, JavaScript |
| Backend | Python, Flask |
| Database | PostgreSQL |
| Containers | Docker |
| Cloud | Amazon Web Services |
| Compute | Amazon ECS, AWS Fargate |
| Database Hosting | Amazon RDS |
| Container Registry | Amazon ECR |
| Infrastructure as Code | Terraform |
| Version Control | Git, GitHub |

## AWS Architecture

The application uses the following components:

1. React frontend served through an Nginx container
2. Flask backend exposing REST API endpoints
3. PostgreSQL database hosted on Amazon RDS
4. Amazon ECS with AWS Fargate for container orchestration
5. Amazon ECR for container image storage
6. AWS networking and security groups for connectivity
7. Terraform for provisioning and managing cloud infrastructure

Both the frontend and backend run as containers within the ECS task.

The backend connects to PostgreSQL for persistent inventory storage.

## Application Functionality

### Inventory Dashboard

Displays the total number of products, available units, inventory valuation, and low-stock items.

### Product Management

Supports adding products with a name, SKU, price, and initial quantity.

### Stock Adjustments

Allows users to increase or decrease inventory while recording the reason for each adjustment.

### Transaction History

Provides a history of stock changes, including previous quantity, updated quantity, reason, and timestamp.

## Deployment and Validation

The application was deployed and tested in an AWS development environment.

Validation included:

- Provisioning AWS resources with Terraform
- Building and deploying Docker container images
- Running the frontend and backend on ECS Fargate
- Initializing the PostgreSQL database schema
- Confirming API connectivity and database health
- Creating a product through the web interface
- Updating product inventory
- Verifying inventory totals and transaction history
- Confirming that data persisted in PostgreSQL

The deployment was subsequently scaled down to reduce ongoing infrastructure costs.

## Engineering Challenges and Lessons

One of the most valuable aspects of this project was integrating independently developed components into a functioning cloud deployment.

Early development focused on individual application components. During integration, additional attention was required around container configuration, service networking, database initialization, and deployment validation.

This reinforced the importance of defining service boundaries, validating integrations early, and designing for observability and troubleshooting throughout development.

## Local Development

The repository contains Docker configuration for running the application locally.

The backend uses Python and Flask, while the frontend uses React.

PostgreSQL provides persistent application storage.

See the Docker Compose configuration and application source files for implementation details.

## Project Status

The core inventory workflow has been implemented and validated in an AWS development environment.

The infrastructure is scaled down when not in use to minimize cloud costs.

## Author

Developed as a personal software engineering project focused on full-stack development, cloud infrastructure, containerization, and deployment automation.
