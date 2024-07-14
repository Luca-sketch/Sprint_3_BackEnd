# Título: API MODERN_CLICK_STORE

## Descrição

Esta API faz parte do projeto Modern Click Store, mas pode ser utilizada em outros projetos. Ela é responsável por armazenar as compras e o cadastro dos usúarios.

## Segurança

Esta API espera uma key no header em determinadas rotas e outras é necessário estar logado.
No arquivo config.env é possivel alterar o valor da key e as configurações de conexão com o banco de dados.

## Tabelas

Nessa aplicação são utilizadas duas tabelas, carrinho e usuario

**Tabela carrinho**

| Nome da Coluna | Tipo       | Descrição                       |
|----------------|------------|---------------------------------|
| id             | Integer    | Chave primária(Auto increment)  |
| Produto        | String(100)| Nome do Produto                 |
| Valor          | String(100)| Valor do Produto                |
| Onda           | String(100)| Descrição da Onda               |
| Token          | String(200)| Token de Identificação          |


**Tabela usuario**

| Nome da Coluna | Tipo       | Descrição                      |
|----------------|------------|--------------------------------|
| id             | Integer    | Chave primária(Auto increment) |
| Email          | String(100)| Email do Usuário               |
| Senha          | String(255)| Senha do Usuário               |
| CEP            | String(20) | CEP do Usuário                 |


## Fluxograma

Este projeto envolve a integração das seções da API (FLASK) com a comunicação com o banco de dados MYSQL.

![Fluxograma da API CEP](https://drive.google.com/uc?export=view&id=1U9g5ff8OsP1tmSop7i7xAdokDXgwdGg0)

## Instruções de Uso

Esta API pode ser utilizada de duas maneiras diferentes: via Docker ou através da instalação tradicional de dependências.

### 1. Docker

Para executar a API utilizando Docker, siga os seguintes passos:

```bash
docker build -t api_modern_click_store .
docker run -d -p 3000:3000 api_modern_click_store
```
### 2. Instalação Tradicional
```bash
 pip install requirements.txt
 python app.py
