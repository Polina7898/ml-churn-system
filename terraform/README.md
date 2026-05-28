# Инфраструктура как код

Terraform поднимает в Yandex Cloud одну виртуальную машину и через cloud-init разворачивает на ней все микросервисы из `docker-compose.yml`.

## Что создаётся

- VPC-сеть и подсеть
- виртуальная машина Ubuntu 22.04, 2 vCPU / 4 ГБ RAM
- публичный IP с NAT
- автоматический запуск Docker + `docker compose up -d --build`

## Запуск

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# отредактируйте terraform.tfvars: токен, cloud_id, folder_id, URL репозитория
terraform init
terraform apply
```

После `apply` Terraform выведет URL всех сервисов. Поднятие занимает 8–12 минут (сборка Docker-образа).

## Удаление

```bash
terraform destroy
```

## Что куда смотрит

| Порт | Сервис |
|---|---|
| 8000 | Churn API (FastAPI) |
| 5000 | MLflow UI |
| 4200 | Prefect UI |
| 9090 | Prometheus |
