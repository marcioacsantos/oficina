# Gestão de Oficina — Equipamentos, Utilizações e Relatórios

Aplicação web para gestão centralizada de equipamentos e materiais de uma
oficina ou laboratório: registo e consulta de equipamentos, controlo de
quem os utiliza e durante quanto tempo, histórico de manutenções, reservas
antecipadas e relatórios exportáveis em PDF.

Projeto final — Ação 25.0373, Técnico/a Especialista em Tecnologias e
Programação de Sistemas de Informação (IEFP).

---

## Índice

1. [Tecnologias](#tecnologias)
2. [Funcionalidades](#funcionalidades)
3. [Estrutura do projeto](#estrutura-do-projeto)
4. [Pré-requisitos](#pré-requisitos)
5. [Instalação e configuração](#instalação-e-configuração)
6. [Executar a aplicação](#executar-a-aplicação)
7. [Contas de acesso (demonstração)](#contas-de-acesso-demonstração)
8. [Variáveis de ambiente](#variáveis-de-ambiente)
9. [Resolução de problemas](#resolução-de-problemas)
10. [Acesso a partir do telemóvel / rede local](#acesso-a-partir-do-telemóvel--rede-local)
11. [Ligar a um MySQL numa máquina virtual](#ligar-a-um-mysql-numa-máquina-virtual)

---

## Tecnologias

| Camada           | Tecnologia                                            |
|-------------------|--------------------------------------------------------|
| Back-end          | Python 3, Flask                                        |
| Base de dados      | MySQL 8 (script compatível com MySQL Workbench)        |
| Front-end          | HTML5, CSS3, Bootstrap 5 (responsivo), Chart.js         |
| Geração de PDF     | ReportLab                                               |
| Autenticação       | Sessões Flask + hashing de password com Werkzeug        |
| Configuração       | Variáveis de ambiente via `.env` (python-dotenv)        |

## Funcionalidades

- **Autenticação e perfis** — login com password encriptada (nunca em texto
  simples) e dois perfis distintos, Administrador e Utilizador, com
  permissões diferenciadas.
- **Gestão de equipamentos** — registo, edição, pesquisa, filtro por estado
  e remoção de equipamentos, com categoria, localização, estado e
  fornecedor associados.
- **Controlo de utilizações** — registo de início/fim de utilização de um
  equipamento, com histórico completo por equipamento.
- **Manutenções** — abertura e conclusão de manutenções, com histórico
  associado ao equipamento.
- **Reservas antecipadas** — só é possível reservar equipamento no estado
  "Disponível"; a aplicação impede reservas sobrepostas e mostra, na lista
  de equipamentos, o horário de início/fim de quem tem uma reserva ativa.
- **Gestão de utilizadores** — criação, ativação/desativação e definição
  de perfil, reservada ao Administrador.
- **Relatórios em PDF** — quatro tipos (geral, por equipamento, por
  utilizador e por manutenções), gerados no servidor com ReportLab e
  disponíveis para download.
- **Painel principal (dashboard)** — indicadores gerais, gráficos
  (estado do parque, categorias, tendência mensal de utilizações, top de
  equipamentos mais usados) e valor do parque de equipamentos, este
  último visível apenas ao perfil Administrador.
- **Interface responsiva** — adaptada a computador e a telemóvel.
- **Tratamento de erros de ligação à base de dados** — se o MySQL estiver
  desligado, com credenciais erradas, ou inacessível, a aplicação mostra
  uma página de erro clara em vez de um erro técnico (ver secção
  [Resolução de problemas](#resolução-de-problemas)).

## Estrutura do projeto

```
oficina/
├── app.py                          # Aplicação Flask (rotas e lógica de negócio)
├── requirements.txt                 # Dependências Python
├── .env.example                     # Modelo de configuração (copiar para .env)
├── database/
│   └── gestao_oficina.sql           # Script de criação da base de dados
├── static/
│   ├── css/style.css                # Estilo visual da aplicação
│   ├── js/app.js                    # Comportamento do lado do cliente
│   └── img/logo.svg                 # Logótipo
└── templates/                       # Páginas HTML (Jinja2)
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── equipamentos_lista.html
    ├── equipamento_form.html
    ├── historico_equipamento.html
    ├── utilizacao_form.html
    ├── utilizacoes_lista.html
    ├── reserva_form.html
    ├── reservas_lista.html
    ├── utilizadores_lista.html
    ├── utilizador_form.html
    ├── relatorios.html
    ├── relatorio_resultado.html
    └── erro.html                    # Página de erro (404 / 403 / 503 / 500)
```

## Pré-requisitos

- Python 3.10 ou superior
- MySQL Server 8.x (local ou numa máquina virtual)
- MySQL Workbench (recomendado, para gerir a base de dados visualmente)

## Instalação e configuração

**1. Criar um ambiente virtual e instalar as dependências**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate      # Linux/Mac

pip install -r requirements.txt
```

**2. Criar a base de dados**

No MySQL Workbench: **File → Open SQL Script...**, seleciona
`database/gestao_oficina.sql` e executa (ícone ⚡). Isto cria a base de
dados `gestao_oficina`, com as tabelas, duas views de apoio a consultas
(`vw_equipamentos_estado`, `vw_utilizacoes_detalhe`) e dados de exemplo.

Ou, pela linha de comandos:

```bash
mysql -u root -p < database/gestao_oficina.sql
```

**3. Configurar a ligação à base de dados**

Copia `.env.example` para `.env` e ajusta os valores conforme o teu
MySQL:

```bash
copy .env.example .env        # Windows
cp .env.example .env           # Linux/Mac
```

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=a_tua_password
DB_NAME=gestao_oficina
```

O ficheiro `.env` **não deve ser submetido ao repositório** (já está
listado no `.gitignore`) — cada pessoa configura o seu próprio.

## Executar a aplicação

```bash
python app.py
```

Por omissão, a aplicação fica disponível em **http://127.0.0.1:3000**.

## Contas de acesso (demonstração)

| Perfil        | Utilizador | Palavra-passe |
|---------------|------------|----------------|
| Administrador | `admin`    | `admin123`     |
| Utilizador    | `user`     | `user123`      |

As palavras-passe são guardadas com hash seguro (`werkzeug.security`),
nunca em texto simples.

## Variáveis de ambiente

| Variável       | Obrigatória | Descrição                                            | Valor por omissão |
|----------------|:-----------:|--------------------------------------------------------|:--------------------:|
| `SECRET_KEY`   | Recomendada | Chave usada para assinar a sessão. Define um valor próprio antes de ir para produção. | chave de desenvolvimento |
| `DB_HOST`      | Sim         | Endereço do servidor MySQL                              | `localhost`          |
| `DB_PORT`      | Não         | Porta do servidor MySQL                                  | `3306`                |
| `DB_USER`      | Sim         | Utilizador da base de dados                              | `root`                |
| `DB_PASSWORD`  | Sim         | Palavra-passe do utilizador da base de dados             | *(vazia)*             |
| `DB_NAME`      | Não         | Nome da base de dados                                    | `gestao_oficina`      |
| `PORT`         | Não         | Porta onde o servidor Flask fica à escuta                | `3000`                |
| `FLASK_DEBUG`  | Não         | `true` em desenvolvimento (recarrega automaticamente e mostra o depurador); define `false` em produção | `true` |

## Resolução de problemas

A aplicação foi preparada para lidar com falhas de ligação à base de
dados de forma clara, em vez de mostrar um erro técnico ao utilizador:

- **MySQL desligado, ou host/porta errados no `.env`** — a aplicação
  aguarda até 5 segundos e mostra a página "Serviço indisponível", com
  a causa provável indicada.
- **Utilizador ou palavra-passe errados** — mensagem específica a indicar
  que as credenciais em `DB_USER`/`DB_PASSWORD` devem ser revistas.
- **Nome da base de dados errado, ou script SQL ainda não executado** —
  mensagem a indicar que a base de dados indicada não existe.
- **Erro `'cryptography' package is required...`** — falta o pacote
  `cryptography`, necessário para o método de autenticação por omissão
  do MySQL 8. Corre `pip install -r requirements.txt` novamente (já está
  incluído) ou, isoladamente, `pip install cryptography`.

> Nota: fechar o **MySQL Workbench** não desliga o servidor MySQL — o
> Workbench é apenas um cliente. O serviço `mysqld` corre em segundo
> plano (normalmente como um serviço do Windows/systemd) mesmo com o
> Workbench fechado, pelo que a aplicação continua a conseguir ligar-se.

Todos estes casos ficam registados na consola onde a aplicação está a
correr (`app.logger.error`), para facilitar o diagnóstico durante o
desenvolvimento.

## Acesso a partir do telemóvel / rede local

A aplicação já corre com `host="0.0.0.0"`, pelo que fica acessível a
partir de outros dispositivos na mesma rede Wi-Fi:

1. No PC onde a aplicação está a correr, descobre o IP local (`ipconfig`
   no Windows ou `ip addr` no Linux).
2. No telemóvel, abre o browser em `http://<IP-do-PC>:3000`
   (ex.: `http://192.168.1.20:3000`).

## Ligar a um MySQL numa máquina virtual

Se o MySQL não está instalado no PC mas sim dentro de uma máquina
virtual (VirtualBox, VMware, etc.):

1. **Descobrir o IP da VM** — dentro da VM: `ip addr` / `hostname -I`
   (Linux) ou `ipconfig` (Windows).
2. **Permitir ligações externas ao MySQL** — no ficheiro de configuração
   do MySQL dentro da VM (`my.cnf`/`mysqld.cnf`), define
   `bind-address = 0.0.0.0` e reinicia o serviço.
3. **Autorizar o utilizador a ligar-se remotamente**:
   ```sql
   CREATE USER 'root'@'%' IDENTIFIED BY 'a_tua_password';
   GRANT ALL PRIVILEGES ON gestao_oficina.* TO 'root'@'%';
   FLUSH PRIVILEGES;
   ```
4. **Modo de rede da VM** — em modo *Bridge* a VM tem IP próprio na rede
   local (mais simples); em modo *NAT* é necessário configurar
   *Port Forwarding* da porta `3306`.
5. **Firewall** — confirma que a porta `3306` está aberta na VM.
6. **Configurar a aplicação** — no `.env`, define `DB_HOST` com o IP da
   VM e a `DB_PASSWORD` correta.
7. **Testar a ligação antes de correr a app** (opcional, mas útil para
   isolar problemas de rede dos problemas da aplicação):
   ```bash
   mysql -h <IP-da-VM> -u root -p gestao_oficina
   ```
