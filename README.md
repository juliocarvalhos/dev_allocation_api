# Dev Allocation API

[![CI](https://github.com/juliocarvalhos/dev-allocation-api/actions/workflows/ci.yml/badge.svg)](https://github.com/juliocarvalhos/dev-allocation-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-5.2%20LTS-0C4B33)
![License](https://img.shields.io/badge/license-MIT-green)

API REST para alocar desenvolvedores em projetos de software de acordo com as tecnologias que dominam,
respeitando o período e as horas planejadas de cada projeto.

Gerentes de projeto cadastram **tecnologias**, **desenvolvedores** e **projetos**. A API garante
que toda **alocação** obedece às regras de negócio, tanto na criação quanto na edição.

## Stack

| Camada | Tecnologia |
| --- | --- |
| Linguagem | Python 3.12 |
| Framework | Django 5.2 LTS + Django REST Framework |
| Autenticação | JWT (`djangorestframework-simplejwt`), com rotação e blacklist de refresh tokens |
| Banco de dados | PostgreSQL 17 |
| Documentação | OpenAPI 3 com `drf-spectacular` (Swagger UI e ReDoc) |
| Infra | Docker, Docker Compose, Gunicorn, WhiteNoise |
| Qualidade | Testes com `unittest`/DRF `APITestCase`, Ruff (lint e formatação), cobertura com `coverage` |
| CI | GitHub Actions: lint, checagem de migrações, validação do schema OpenAPI e testes no PostgreSQL |

## Regras de negócio

| Regra | Como é garantida |
| --- | --- |
| **Tecnologias**: o desenvolvedor precisa dominar pelo menos uma tecnologia exigida pelo projeto. | Interseção feita no banco (`technologies.filter(id__in=...)`). |
| **Período**: horas só podem ser alocadas enquanto o projeto está em andamento (`data_inicial <= hoje <= data_final`). | Usa `timezone.localdate()` para respeitar o fuso configurado. |
| **Horas**: a soma das horas alocadas em um projeto não pode passar das horas planejadas. | Soma feita com `aggregate(Sum)`. Na edição, a própria alocação é excluída da soma. |
| **Horas planejadas**: calculadas automaticamente como `dias do período (inclusive) × 8h`. | Campo somente leitura, recalculado no `save()`. |
| **Consistência do projeto**: a data final não pode ser anterior à inicial, e o projeto não pode ser encurtado para menos horas do que já foram alocadas. | Validação no `ProjectSerializer`. |
| **Autenticação**: todos os endpoints de negócio exigem um JWT válido. | `IsAuthenticated` como permissão padrão. |

## Como rodar

### Com Docker (recomendado)

```bash
git clone https://github.com/juliocarvalhos/dev-allocation-api.git
cd dev-allocation-api
cp .env.example .env          # ajuste DJANGO_SECRET_KEY
docker compose up --build
```

As migrações rodam automaticamente na subida. Crie um usuário para obter tokens:

```bash
docker compose exec api python manage.py createsuperuser
```

A API fica em <http://localhost:8000> e a raiz redireciona para o Swagger.
Se a porta 8000 estiver ocupada, use `API_PORT=8080 docker compose up`.

### Localmente

Requer Python 3.12 e um PostgreSQL acessível (os dados de conexão ficam no `.env`).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Variáveis de ambiente

| Variável | Descrição | Padrão |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Chave secreta do Django. Obrigatória com `DEBUG` desligado. | — |
| `DJANGO_DEBUG` | Ativa o modo debug. | `False` |
| `DJANGO_ALLOWED_HOSTS` | Hosts aceitos, separados por vírgula. | `localhost,127.0.0.1` |
| `DJANGO_CORS_ALLOWED_ORIGINS` | Origens liberadas para CORS, separadas por vírgula. | vazio |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Credenciais do banco. | `dev_allocation` |
| `POSTGRES_HOST` / `POSTGRES_PORT` | Endereço do banco (no Compose o host é sempre `db`). | `localhost` / `5432` |

Para gerar uma chave secreta:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

## Uso da API

A documentação interativa fica em [`/api/docs/`](http://localhost:8000/api/docs/) (Swagger) e
[`/api/redoc/`](http://localhost:8000/api/redoc/). O schema OpenAPI fica em `/api/schema/`.

### Autenticação

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "sua-senha"}'
# => {"refresh": "...", "access": "..."}
```

Envie o token de acesso no header `Authorization: Bearer <access>`. Ele vale 30 minutos e é
renovado em `POST /api/token/refresh/`.

### Endpoints

| Recurso | Rotas | Observações |
| --- | --- | --- |
| Tecnologias | `GET/POST /api/technologies/` · `GET/PUT/PATCH/DELETE /api/technologies/{id}/` | Nome único. |
| Desenvolvedores | `GET/POST /api/developers/` · `GET/PUT/PATCH/DELETE /api/developers/{id}/` | `technologies` recebe uma lista de IDs. |
| Projetos | `GET/POST /api/projects/` · `GET/PUT/PATCH/DELETE /api/projects/{id}/` | `planned_hours` é calculado. |
| Alocações | `GET/POST /api/allocations/` · `GET/PUT/PATCH/DELETE /api/allocations/{id}/` | Aplica as regras de negócio. |

As listagens são paginadas (20 itens por página).

### Exemplo de regra violada

```bash
curl -X POST http://localhost:8000/api/allocations/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"project": 1, "developer": 1, "hours": 500}'
```

```json
{
  "non_field_errors": [
    "Allocating 500 hours exceeds the planned hours for the project 'Backend'. Currently allocated: 0 hours, planned: 88 hours."
  ]
}
```

## Testes

Os testes ficam em [`api/tests/`](api/tests/) e cobrem:

- **Regras de alocação** ([`test_allocation_rules.py`](api/tests/test_allocation_rules.py)): tecnologia, período (inclusive os limites), limite de horas (somando vários desenvolvedores), edição sem contagem dupla e `PATCH` que tenta burlar as regras.
- **Model** ([`test_models.py`](api/tests/test_models.py)): cálculo das horas planejadas.
- **API** ([`test_api.py`](api/tests/test_api.py)): autenticação JWT, fluxo CRUD completo e erros de regra via HTTP.

```bash
coverage run manage.py test
coverage report
ruff check . && ruff format --check .
```

Com Docker: `docker compose exec api python manage.py test`.

## Decisões técnicas

- **Regras no serializer.** As validações ficam no `AllocationSerializer` e valem para `POST`,
  `PUT` e `PATCH`. Na atualização parcial, os campos ausentes são preenchidos com os valores
  atuais, para que nenhum `PATCH` contorne uma regra.
- **Agregação no banco.** A soma de horas e a checagem de tecnologias em comum são feitas com
  consultas SQL (`Sum`, `filter(id__in=...)`), sem carregar os registros em memória.
- **Horas planejadas derivadas.** `planned_hours` é calculado a partir do período e é somente leitura
  na API, o que evita divergência entre datas e horas.
- **Configuração por ambiente.** Segredos e parâmetros de infraestrutura vêm de variáveis de
  ambiente (12-factor). Sem `DJANGO_SECRET_KEY`, a aplicação não sobe em modo de produção.
- **JWT de vida curta.** Access token de 30 minutos, refresh token de 1 dia, com rotação e blacklist.
- **Imagem enxuta e sem root.** A imagem é `python:3.12-slim`, roda com um usuário sem privilégios e
  serve via Gunicorn. O WhiteNoise entrega os arquivos estáticos do admin.

## Estrutura

```
├── api/
│   ├── models.py          # Technology, Developer, Project, Allocation
│   ├── serializers.py     # validações das regras de negócio
│   ├── views.py           # ViewSets do DRF
│   └── tests/             # testes de model, regras e API
├── dev_allocation/        # settings, urls, wsgi
├── .github/workflows/     # pipeline de CI
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).
