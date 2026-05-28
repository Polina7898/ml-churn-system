terraform {
  required_version = ">= 1.5.0"
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = "~> 0.110"
    }
  }
}

provider "yandex" {
  token     = var.yc_token
  cloud_id  = var.yc_cloud_id
  folder_id = var.yc_folder_id
  zone      = var.yc_zone
}

data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

resource "yandex_vpc_network" "ml_network" {
  name = "ml-churn-network"
}

resource "yandex_vpc_subnet" "ml_subnet" {
  name           = "ml-churn-subnet"
  zone           = var.yc_zone
  network_id     = yandex_vpc_network.ml_network.id
  v4_cidr_blocks = ["10.10.0.0/24"]
}

resource "yandex_compute_instance" "ml_vm" {
  name        = "ml-churn-vm"
  platform_id = "standard-v3"
  zone        = var.yc_zone

  resources {
    cores         = var.vm_cores
    memory        = var.vm_memory_gb
    core_fraction = 50
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = 20
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.ml_subnet.id
    nat       = true
  }

  metadata = {
    user-data = templatefile("${path.module}/cloud-init.yaml", {
      repo_url = var.repo_url
    })
    ssh-keys = "ubuntu:${file(var.ssh_public_key_path)}"
  }

}

output "vm_external_ip" {
  description = "Внешний IP виртуальной машины"
  value       = yandex_compute_instance.ml_vm.network_interface.0.nat_ip_address
}

output "api_url" {
  description = "URL API сервиса"
  value       = "http://${yandex_compute_instance.ml_vm.network_interface.0.nat_ip_address}:8000"
}

output "mlflow_url" {
  description = "URL MLflow UI"
  value       = "http://${yandex_compute_instance.ml_vm.network_interface.0.nat_ip_address}:5000"
}

output "prefect_url" {
  description = "URL Prefect UI"
  value       = "http://${yandex_compute_instance.ml_vm.network_interface.0.nat_ip_address}:4200"
}

output "prometheus_url" {
  description = "URL Prometheus"
  value       = "http://${yandex_compute_instance.ml_vm.network_interface.0.nat_ip_address}:9090"
}
