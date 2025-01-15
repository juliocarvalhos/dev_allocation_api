# Gerenciamento e Alocação de Desenvolvedores - README

Este é um projeto de uma API desenvolvida em Django para gerenciar e realizar a alocação de desenvolvedores de software em projetos. A API auxilia gerentes de projeto a alocar desenvolvedores de forma eficiente e de acordo com suas especializações. Também gerencia informações relacionadas às tecnologias, programadores, projetos e suas respectivas alocações.

---

## Tecnologias Utilizadas
- **Backend**: Django, Django REST Framework
- **Banco de Dados**: PostgreSQL

---

## Requisitos

Certifique-se de ter os seguintes softwares instalados em sua máquina:
- Python (versão 3.8 ou superior)
- PostgreSQL
- Git

---

## Passo a Passo para Instalar e Executar Localmente

### 1. Clonar o Repositório

```bash
$ git clone https://github.com/juliocarvalhos/dev_allocation.git
$ cd dev_allocation
```

### 2. Criar e Ativar um Ambiente Virtual

```bash
$ python3 -m venv venv
$ source venv/bin/activate  # Linux/MacOS
# ou
$ venv\Scripts\activate  # Windows
```

### 3. Instalar as Dependências

```bash
$ pip install -r requirements.txt
```

### 4. Configurar o Banco de Dados PostgreSQL

1. Certifique-se de que o PostgreSQL esteja em execução.
2. Crie um banco de dados para a aplicação:

```sql
CREATE DATABASE developer_allocation;
CREATE USER dev_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE developer_allocation TO dev_user;
```

3. Crie o arquivo `settings.py` com as configurações do banco:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'developer_allocation',
        'USER': 'dev_user',
        'PASSWORD': 'dev_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Realizar Migrações do Banco de Dados

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

### 6. Criar um Superusuário

Necessário para autenticação com JWT

```bash
$ python manage.py createsuperuser
```

### 7. Executar o Servidor Local

```bash
$ python manage.py runserver
```

A API estará disponível em [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## Configuração de Variáveis de Ambiente

Recomenda-se o uso de um arquivo `.env` para gerenciar as variáveis de ambiente. Exemplo de configuração:

```env
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_NAME=developer_allocation
DATABASE_USER=dev_user
DATABASE_PASSWORD=dev_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

Atualize o `settings.py` para usar essas variáveis:

```python
from dotenv import load_dotenv
import os

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}
```

---

## Testando a API

### 1. Instalar o Cliente HTTP
Use ferramentas como [Postman](https://www.postman.com/) ou [Insomnia](https://insomnia.rest/) para testar a API.

### 2. Endpoints Disponíveis
Consulte a documentação dos endpoints [Aqui](https://127.0.0.1:8000/api/docs)

---

Veja em detalhes o [Desafio proposto](desafio_proposto.md)

---

## Possíveis Problemas e Soluções

1. **Erro de conexão com o banco de dados**:
   - Verifique se o PostgreSQL está em execução.
   - Confirme as credenciais no `settings.py` ou `.env`.

2. **Erro ao instalar dependências**:
   - Certifique-se de que o ambiente virtual esteja ativo.
   - Atualize o `pip`: `$ pip install --upgrade pip`.

---

## Licença

Este projeto é distribuído sob a Licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.


