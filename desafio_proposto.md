## API para alocação de desenvolvedores

Você foi contratado para desenvolver uma API responsável por gerenciar e realizar a alocação de desenvolvedores de software em projetos. Essa aplicação será utilizada por gerentes de projeto para garantir que desenvolvedores sejam alocados de forma eficiente e de acordo com suas especializações. Além disso, será necessário gerenciar as informações relacionadas às tecnologias, programadores, projetos e suas respectivas alocações.

## Requisitos

### Gerenciar Tecnologias
- Deve ser possível criar, atualizar, listar e remover tecnologias.
- Cada tecnologia possui os seguintes atributos:
  - **ID**: Identificador único da tecnologia (gerado automaticamente).
  - **Nome**: Nome da tecnologia (ex.: "Python", "JavaScript").

### Gerenciar Programadores
- Deve ser possível criar, atualizar, listar e remover programadores.
- Cada programador possui os seguintes atributos:
  - **ID**: Identificador único do programador (gerado automaticamente).
  - **Nome**: Nome do programador.
  - **Tecnologias**: Lista das tecnologias que o programador domina.

### Gerenciar Projetos
- Deve ser possível criar, atualizar, listar e remover projetos.
- Cada projeto possui os seguintes atributos:
  - **ID**: Identificador único do projeto (gerado automaticamente).
  - **Nome**: Nome do projeto.
  - **Data Inicial**: Data de início do projeto.
  - **Data Final**: Data de término do projeto.
  - **Tecnologias**: Lista de tecnologias necessárias para o projeto.

### Gerenciar Alocações de Desenvolvedores em Projetos
- Deve ser possível criar, atualizar, listar e remover alocações.
- Cada alocação possui os seguintes atributos:
  - **ID**: Identificador único da alocação (gerado automaticamente).
  - **Projeto**: O projeto em que o desenvolvedor será alocado.
  - **Desenvolvedor**: O desenvolvedor que será alocado.
  - **Horas**: Quantidade de horas alocadas.

## Regras de Negócio

### Validação de Tecnologias
- Um desenvolvedor só pode ser alocado em um projeto se ele possuir pelo menos uma tecnologia que o projeto exige.

### Validação de Período
- Horas planejadas para o projeto só podem ser distribuídas dentro do intervalo definido por **Data Inicial** e **Data Final**.

### Validação de Horas
- O total de horas alocadas para todos os desenvolvedores em um projeto não pode ultrapassar as horas planejadas para o projeto.

### Autenticação Obrigatória
- Todas as operações da API devem ser restritas a usuários autenticados.
- A API deve implementar um sistema de autenticação (como JWT, OAuth2 ou outro mecanismo seguro).

## Entrega Esperada

### Implementação da API
- Utilize Python + Django para a implementação da API.

### Banco de Dados
- Utilize o Postgres para armazenar as informações necessárias.

### Documentação
- A documentação deve conter um passo a passo detalhado para instalar e executar a aplicação localmente. (**README**)
- É desejável que a aplicação também inclua uma documentação de API utilizando Swagger/OpenAPI.

### Dockerização
- É desejável que a aplicação seja fornecida com suporte a Docker, incluindo:
  - **Dockerfile** para build da aplicação.
  - **docker-compose.yml** para orquestração do ambiente completo (incluindo banco de dados).

### Testes Unitários
- É desejável que a aplicação contenha testes unitários cobrindo as seguintes regras:
  - Validação de tecnologias do desenvolvedor ao alocá-lo em um projeto.
  - Validação de períodos para horas planejadas.
  - Validação do limite de horas alocadas.

## Endpoints

- **Tecnologias**: Endpoints para criar, atualizar, listar e excluir tecnologias.
- **Programadores**: Endpoints para criar, atualizar, listar e excluir programadores.
- **Projetos**: Endpoints para criar, atualizar, listar e excluir projetos, além de distribuir horas planejadas.
- **Alocações**: Endpoints para criar, listar e remover alocações, com as validações mencionadas acima.

## Validações
- Certifique-se de implementar as validações das regras de negócio mencionadas anteriormente.
