# ML-система для предсказания оттока клиентов

Сервис, который по данным клиента телекома говорит, насколько вероятно, что он скоро уйдёт. Под капотом GradientBoosting на sklearn, наружу торчит REST-API на FastAPI. Всё упаковано в Docker, оркестрация обучения через Prefect, эксперименты логируются в MLflow, метрики собирает Prometheus.

Делалось как полноценная ML-система с заявленным уровнем зрелости 2 (есть и оркестратор, и трекинг экспериментов, не только сервинг).

## Что внутри

Четыре микросервиса в одном `docker-compose.yml`:

- **Churn API** на FastAPI, порт 8000. Эндпоинты `/health`, `/predict`, `/metrics`, плюс автоматический Swagger на `/docs`
- **MLflow** на 5050 снаружи (внутри сети 5000) — трекинг экспериментов и model registry
- **Prefect** на 4200 — оркестратор пайплайна обучения
- **Prometheus** на 9090 — собирает метрики с Churn API

Не лепила всё в один монолитный сервис специально, потому что в задании уровень 2 требует именно разделения оркестратора и трекинга экспериментов как разных компонентов.

## Структура

```
.
├── manifest.md                      манифест ML-системы со всеми 12 разделами
├── Dockerfile                       сборка churn-api
├── docker-compose.yml               все 4 сервиса
├── requirements.txt
├── src/
│   ├── data.py                       синтетический датасет
│   ├── features.py                   feature store
│   ├── train.py                      обучение модели + лог в MLflow
│   ├── pipeline.py                   Prefect-флоу
│   ├── serve.py                      FastAPI
│   └── mdd_analysis.py               статистический тест для ADR
├── tests/test_api.py                 pytest
├── monitoring/prometheus.yml
├── terraform/                        IaC для Yandex Cloud
├── .github/workflows/ci-cd.yml       CI/CD
└── docs/
    ├── sli_slo.md
    ├── screenshots/                   скрины работающей системы
    └── adr/001-latency-optimization.md
```

## Запустить локально

```bash
docker compose up -d --build
docker ps
```

Дальше можно потыкать:

- http://localhost:8000/health
- http://localhost:8000/docs (Swagger с тремя эндпоинтами)
- http://localhost:5050 (MLflow)
- http://localhost:4200 (Prefect)
- http://localhost:9090 (Prometheus)

Предсказание:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"tenure": 12, "monthly_charges": 70.5, "total_charges": 846, "contract": 0, "internet_service": 1, "payment_method": 2}'
```

Должен вернуться JSON типа `{"churn_probability": 0.83, "action": "urgent_retention_offer"}`.

## Развернуть в облаке

Использовала Yandex Cloud, провайдер для Terraform у них хороший и доступен из России. Конфиг лежит в `terraform/`.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# заполнить yc_token, yc_cloud_id, yc_folder_id, repo_url
terraform init
terraform apply
```

Через 10 минут будет публичный IP, на нём заработают все 4 сервиса. Cloud-init на ВМ сам ставит Docker, клонирует репозиторий и поднимает compose. Полностью без ручных действий, в духе infrastructure as code.

Удалить инфраструктуру:

```bash
terraform destroy
```

## Локальные команды

- обучить модель один раз: `python -m src.train`
- запустить весь пайплайн через Prefect: `python -m src.pipeline`
- прогнать статистический анализ для ADR: `python -m src.mdd_analysis`
- тесты: `pytest -v tests/`

## CI/CD

GitHub Actions при пуше в main: ставит зависимости, инициализирует фича-стор, обучает модель, прогоняет pytest, запускает MDD-анализ, собирает Docker-образ и делает smoke-тест собранного контейнера через `/health`. Файл воркфлоу в `.github/workflows/ci-cd.yml`.

## Что ещё стоит знать

Модель учится на синтетических данных, сгенерированных в `src/data.py` (имитирую датасет Telco Customer Churn). Для реального продакшена сюда нужно подключить выгрузку из CRM, но для демонстрации архитектуры синтетика норм.

Quality gate стоит в `src/train.py` — если ROC-AUC меньше 0.80, обучение падает с ошибкой и плохая модель не уезжает в registry. На реальном датасете порог стоит поднять.
