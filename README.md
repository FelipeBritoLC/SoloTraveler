# Solo Traveler 🧳

Projeto acadêmico da disciplina de **Desenvolvimento Ágil (RAD com Django)**.

Aplicação web para planejamento de roteiros de viagens independentes: o usuário
cadastra suas viagens, organiza atividades dia após dia (com categoria, horário e
custo) e pode tornar seu roteiro público para inspirar outros viajantes em um feed
paginado e filtrável por categoria.


---

## 1. Sumário

- [2. Funcionalidades implementadas](#2-funcionalidades-implementadas)
- [3. Requisitos obrigatórios da disciplina — onde estão no código](#3-requisitos-obrigatórios-da-disciplina--onde-estão-no-código)
- [4. Modelo de dados](#4-modelo-de-dados)
- [5. Estrutura de pastas](#5-estrutura-de-pastas)
- [6. Requisitos para rodar o projeto](#6-requisitos-para-rodar-o-projeto)
- [7. Passo a passo para rodar localmente](#7-passo-a-passo-para-rodar-localmente)
- [8. Usuário de administração (opcional)](#8-usuário-de-administração-opcional)
- [9. Como usar a aplicação](#9-como-usar-a-aplicação)
- [10. API REST (Django REST Framework)](#10-api-rest-django-rest-framework)
- [11. Upload de foto de capa](#11-upload-de-foto-de-capa)
- [12. Internacionalização (i18n)](#12-internacionalização-i18n)
- [13. Testes automatizados](#13-testes-automatizados)
- [14. Possíveis problemas e soluções](#14-possíveis-problemas-e-soluções)

---

## 2. Funcionalidades implementadas

- Cadastro e login de usuários.
- CRUD completo de **Viagens** (título, destino, data de início/fim, visibilidade
  pública/privada, **foto de capa**).
- CRUD completo de **Atividades** dentro de cada viagem (nome, categoria, data/hora,
  custo estimado, descrição).
- Cálculo automático do **custo total** da viagem, somando o custo de suas atividades.
- **Feed público** paginado com as viagens marcadas como públicas, com filtro por
  categoria de atividade.
- Apenas o **dono** de uma viagem pode editá-la ou excluí-la (assim como suas
  atividades).
- **API REST** completa (Django REST Framework) para viagens, atividades e
  categorias.
- Interface disponível em **Português** e **Inglês** (i18n), com seletor de idioma
  no cabeçalho.
- **Testes automatizados** cobrindo regras de negócio, permissões e a API.

---

## 3. Requisitos obrigatórios da disciplina — onde estão no código

| Requisito | Onde foi implementado |
|---|---|
| **Arquitetura MVT** | Padrão do Django: `travels/models.py` (Model), `travels/templates/` (Template), `travels/views.py` (View). |
| **Paginação** | `FeedPublicoView` e `MinhasViagensView` em `travels/views.py` (`paginate_by = 6`), template `travels/_paginacao.html`. Na API, `ApiPagination` em `travels/api_views.py`. |
| **Autenticação** | `django.contrib.auth` + `MinhaLoginView`/`registrar()` em `travels/views.py`, formulário `RegistroForm` em `travels/forms.py`, templates em `templates/registration/`. |
| **Autorização** | `LoginRequiredMixin` + `UserPassesTestMixin` (`ViagemDonoMixin`, `AtividadeDonoMixin`) em `travels/views.py`, garantindo que só o dono edite/exclua seus dados. Na API, a permissão `IsOwnerOrReadOnly` em `travels/api_views.py`. |
| **API REST com DRF** | `travels/serializers.py`, `travels/api_views.py`, `travels/api_urls.py`, montada em `/api/`. |
| **Testes automatizados** | `travels/tests.py` — regras de negócio (custo total, validação de datas), permissões e endpoints da API. |
| **i18n** | `LocaleMiddleware`, `LANGUAGES`, `LOCALE_PATHS` em `solotraveler/settings.py`; `{% trans %}`/`{% blocktrans %}` nos templates; arquivos de tradução em `locale/pt_BR` e `locale/en`; seletor de idioma no `base.html`. |

Além disso, os requisitos funcionais (RF01 a RF11) descritos na apresentação também
foram atendidos — a tabela acima mostra o mapeamento dos requisitos técnicos da
disciplina, e o restante do modelo/views cobre os requisitos funcionais do sistema.

---

## 4. Modelo de dados

Segue o diagrama entidade-relacionamento apresentado na pré-defesa, usando a tabela
nativa de usuários do Django:

```
usuarios (User, do Django)
   1 ────< viagens >──── N atividades
                              N
                              │
                              1
                          categorias
```

- **Viagem**: `usuario` (FK), `titulo`, `destino`, `data_inicio`, `data_fim`, `publica`.
- **Atividade**: `viagem` (FK), `categoria` (FK), `nome`, `data_hora`, `custo_estimado`, `descricao`.
- **Categoria**: `nome`.

---

## 5. Estrutura de pastas

```
solotraveler_project/
├── manage.py
├── requirements.txt
├── solotraveler/            # configurações do projeto
│   ├── settings.py
│   └── urls.py
├── travels/                 # app principal (toda a regra de negócio)
│   ├── models.py            # Categoria, Viagem, Atividade
│   ├── views.py             # views HTML (MVT)
│   ├── forms.py
│   ├── urls.py
│   ├── serializers.py       # DRF
│   ├── api_views.py         # DRF
│   ├── api_urls.py          # DRF
│   ├── admin.py
│   ├── tests.py             # testes automatizados
│   └── templates/travels/
├── templates/                # base.html e templates de login/registro
│   ├── base.html
│   └── registration/
└── locale/                   # traduções (i18n)
    ├── pt_BR/LC_MESSAGES/
    └── en/LC_MESSAGES/
```

---

## 6. Requisitos para rodar o projeto

- **Python 3.10 ou superior** instalado (`python3 --version`).
- **pip** instalado.
- Acesso à internet apenas na primeira vez, para instalar as dependências (e, ao
  usar a interface, para carregar as fontes do Google Fonts usadas no visual).
- Sistema operacional: Windows, Linux ou macOS (o projeto usa apenas Django, DRF e
  Pillow — sem dependências específicas de sistema operacional).

Não é necessário instalar nenhum banco de dados separado: o projeto usa **SQLite**,
que já vem embutido no Python, e o arquivo do banco (`db.sqlite3`) é criado
automaticamente.

---

## 7. Passo a passo para rodar localmente

### 7.1. Extrair o projeto

Extraia o `.zip` recebido em uma pasta de sua preferência. Você deverá ver a pasta
`solotraveler_project/` com os arquivos descritos acima.

### 7.2. Criar e ativar um ambiente virtual (recomendado)

No terminal, dentro da pasta `solotraveler_project`:

**Windows (PowerShell):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Você saberá que o ambiente está ativo porque `(venv)` aparecerá no início da linha
do terminal.

### 7.3. Instalar as dependências

```bash
pip install -r requirements.txt
```

Isso instalará o Django, o Django REST Framework e o **Pillow** (biblioteca
necessária para o Django processar upload de imagens) nas versões usadas no
desenvolvimento do projeto.

### 7.4. Aplicar as migrações do banco de dados

```bash
python manage.py migrate
```

Esse comando cria o arquivo `db.sqlite3` com todas as tabelas necessárias
(usuários, viagens, atividades, categorias, etc.).

### 7.5. (Opcional, mas recomendado) Compilar as traduções

Os arquivos de tradução já vêm compilados no projeto (`.mo`), mas caso você edite
algum texto traduzido ou os arquivos `.mo` não estejam presentes, é necessário ter
o **gettext** instalado e rodar:

```bash
python manage.py compilemessages
```

> No Windows, o gettext pode ser instalado seguindo o guia oficial do Django:
> https://docs.djangoproject.com/en/stable/topics/i18n/translation/#gettext-on-windows
> No Linux (Ubuntu/Debian): `sudo apt-get install gettext`
> No macOS (com Homebrew): `brew install gettext`

### 7.6. Criar um superusuário (para acessar o /admin)

```bash
python manage.py createsuperuser
```

Preencha usuário, e-mail (opcional) e senha quando solicitado.

### 7.7. Rodar o servidor de desenvolvimento

```bash
python manage.py runserver
```

O terminal mostrará algo como:

```
Starting development server at http://127.0.0.1:8000/
```

### 7.8. Acessar a aplicação

Abra o navegador em:

- **Site (feed público):** http://127.0.0.1:8000/
- **Painel de administração:** http://127.0.0.1:8000/pt-br/admin/ (login com o
  superusuário criado no passo 7.6)
- **API REST:** http://127.0.0.1:8000/api/

> A raiz `/` redireciona para o idioma padrão (`/pt-br/`). Para testar em inglês,
> acesse `http://127.0.0.1:8000/en/` ou use o seletor de idioma no topo da página.

---

## 8. Usuário de administração (opcional)

Se você não quiser criar um superusuário manualmente, pode simplesmente se
**registrar pela própria interface** (`/registrar/`) e usar a aplicação como um
usuário comum — isso já é suficiente para testar todas as funcionalidades de
viagens/atividades. O superusuário só é necessário para acessar `/admin/`.

---

## 9. Como usar a aplicação

1. Acesse a página inicial — o **feed público** com roteiros de outros usuários.
2. Clique em **"Criar conta"** e cadastre-se.
3. Após logar, clique em **"Nova viagem"** e preencha título, destino e datas.
   Marque **"pública"** se quiser que ela apareça no feed.
4. Na página de detalhe da viagem, clique em **"+ Adicionar atividade"** para
   cadastrar cada etapa do roteiro (categoria, data/hora, custo).
   - Se a data da atividade estiver fora do período da viagem, o sistema mostrará
     um erro de validação.
5. O **custo total** da viagem é somado automaticamente a partir das atividades.
6. Em **"Minhas viagens"** você vê e gerencia (edita/exclui) apenas as suas
   próprias viagens.
7. No **feed público**, use o filtro de categoria para encontrar roteiros de
   interesse (ex: só viagens com atividades de "Gastronomia").

---

## 10. API REST (Django REST Framework)

Endpoints disponíveis a partir de `/api/`:

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/viagens/` | Lista viagens públicas (+ as suas, se autenticado). Paginado. |
| POST | `/api/viagens/` | Cria uma viagem (requer login). |
| GET | `/api/viagens/{id}/` | Detalha uma viagem. |
| PUT/PATCH | `/api/viagens/{id}/` | Edita (só o dono). |
| DELETE | `/api/viagens/{id}/` | Exclui (só o dono). |
| GET/POST | `/api/atividades/` | Lista/cria atividades. |
| PUT/PATCH/DELETE | `/api/atividades/{id}/` | Edita/exclui atividade (só o dono da viagem). |
| GET | `/api/categorias/` | Lista categorias (somente leitura). |

A API usa **autenticação por sessão** do Django (`SessionAuthentication`). Para
testá-la autenticado usando o navegador, faça login pela interface web normal
(`/pt-br/login/`) e depois acesse os endpoints da API — a sessão será reaproveitada
e a própria interface navegável do DRF (*Browsable API*) permitirá enviar
requisições POST/PUT/DELETE diretamente pelo navegador.

---

## 11. Upload de foto de capa

Ao criar ou editar uma viagem, o usuário pode enviar uma **foto de capa** (campo
opcional). Ela é usada em três lugares:

- No **feed público**, como a imagem principal de cada post (proporção 4:5).
- Em **"Minhas viagens"**, como miniatura na grade estilo perfil.
- No **detalhe da viagem**, como imagem de destaque no topo da página.

As fotos enviadas ficam salvas na pasta `media/viagens/AAAA/MM/` (criada
automaticamente) e são servidas pelo próprio Django durante o desenvolvimento
(`MEDIA_URL`/`MEDIA_ROOT` em `solotraveler/settings.py`, rota adicionada em
`solotraveler/urls.py`). Se nenhuma foto for enviada, um ícone ilustrativo aparece
no lugar automaticamente — não é obrigatório fazer upload para publicar uma viagem.

> Isso exige a biblioteca **Pillow**, já incluída no `requirements.txt`.

## 12. Internacionalização (i18n)

- Idiomas disponíveis: **Português (pt-br)**, idioma padrão, e **Inglês (en)**.
- O idioma atual aparece como prefixo na URL (`/pt-br/...` ou `/en/...`).
- Pode ser trocado pelo seletor no topo direito de qualquer página.
- As traduções ficam em `locale/<idioma>/LC_MESSAGES/django.po` (texto-fonte) e
  `django.mo` (versão compilada, usada em tempo de execução).
- Caso adicione novos textos com `{% trans %}` nos templates, gere/atualize os
  arquivos de tradução com:
  ```bash
  python manage.py makemessages -l pt_BR -l en
  ```
  e depois compile novamente com `python manage.py compilemessages`.

---

## 13. Testes automatizados

Para rodar todos os testes do projeto:

```bash
python manage.py test
```

O que é testado (arquivo `travels/tests.py`):

- **Regras de negócio:** cálculo automático do custo total da viagem (RF07);
  validação de que a data de uma atividade precisa estar dentro do período da
  viagem (RF10).
- **Permissões (RF11):** um usuário anônimo não consegue acessar a tela de edição
  de uma viagem; um usuário "B" não consegue editar/excluir a viagem de um
  usuário "A"; o próprio dono consegue editar normalmente.
- **Feed público:** garante que somente viagens públicas aparecem no feed e que a
  paginação está funcionando (6 itens por página).
- **API REST:** listagem pública sem autenticação funciona; criação de viagem sem
  login é negada (403); criação autenticada funciona e associa a viagem ao usuário
  logado.

---

## 14. Possíveis problemas e soluções

- **Erro `ModuleNotFoundError: No module named 'django'`**
  → O ambiente virtual não está ativado ou as dependências não foram instaladas.
  Rode novamente os passos 7.2 e 7.3.

- **Página em branco/erro 404 ao acessar `http://127.0.0.1:8000/`**
  → Confirme se o servidor (`python manage.py runserver`) está rodando e sem
  erros no terminal. A raiz redireciona para `/pt-br/`.

- **Textos aparecem sem tradução em inglês**
  → Os arquivos `.mo` podem não ter sido gerados. Instale o `gettext` (veja passo
  7.5) e rode `python manage.py compilemessages`.

- **Erro ao rodar `createsuperuser` sobre senha muito simples**
  → O Django valida a força da senha por padrão; escolha uma senha com pelo menos
  8 caracteres, que não seja só números.

- **Quero recomeçar do zero (banco de dados limpo)**
  → Apague o arquivo `db.sqlite3` e rode `python manage.py migrate` novamente.
