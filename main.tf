terraform {
  backend "s3" {
    bucket         = "bhargav-terraform-state-bucket" # Use the name from Step 1
    key            = "state/terraform.tfstate"
    region         = "ap-south-1"
  }
}
#testing
# 1. SET UP THE TWO REGIONS
provider "aws" {
  alias  = "mumbai"
  region = "ap-south-1"
}

provider "aws" {
  alias  = "us_east"
  region = "us-east-1"
}

# 2. CREATE THE PRIMARY SERVER (Mumbai)
resource "aws_instance" "primary" {
  provider      = aws.mumbai
  ami           = "ami-0dee22c13ea7a9a67" 
  instance_type = "t3.micro"
  
  # This script disables the internal firewall so pings work immediately
  user_data = <<-EOF
              #!/bin/bash
              sudo ufw disable
              sudo systemctl stop ufw
              EOF

  tags = {
    Name = "Primary-Mumbai-Server"
  }
}

# 3. CREATE THE BACKUP SERVER (USA) - Optimized with FinOps
resource "aws_instance" "backup" {
  provider      = aws.us_east
  ami           = "ami-0453ec754f44f9a4a" 
  instance_type = "t3.micro"

  # --- NEW FINOPS ADDITION ---
  instance_market_options {
    market_type = "spot"
    spot_options {
      max_price = "0.005" # Bid price to ensure cost savings
    }
  }
  # ---------------------------

  user_data = <<-EOF
              #!/bin/bash
              sudo ufw disable
              sudo systemctl stop ufw
              EOF

  tags = {
    Name = "Backup-USA-Server"
    CostCenter = "FinOps-Demo"
  }
}

# --- OUTPUTS (Used by Python script to fetch data automatically) ---

output "primary_server_ip" {
  description = "The public IP of the Mumbai server"
  value       = aws_instance.primary.public_ip
}

output "backup_server_ip" {
  description = "The public IP of the USA server"
  value       = aws_instance.backup.public_ip
}

output "primary_server_id" {
  description = "The ID of the Mumbai server for the stop command"
  value       = aws_instance.primary.id
}

output "backup_server_id" {
  description = "The ID of the USA server"
  value       = aws_instance.backup.id
}