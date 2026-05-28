variable "yc_token" {
  description = "OAuth-токен Yandex Cloud"
  type        = string
  sensitive   = true
}

variable "yc_cloud_id" {
  description = "ID облака"
  type        = string
}

variable "yc_folder_id" {
  description = "ID каталога"
  type        = string
}

variable "yc_zone" {
  description = "Зона доступности"
  type        = string
  default     = "ru-central1-a"
}

variable "vm_cores" {
  description = "Количество vCPU"
  type        = number
  default     = 2
}

variable "vm_memory_gb" {
  description = "Память ВМ, ГБ"
  type        = number
  default     = 4
}

variable "ssh_public_key_path" {
  description = "Путь к публичному SSH-ключу"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "repo_url" {
  description = "URL Git-репозитория с проектом"
  type        = string
}
