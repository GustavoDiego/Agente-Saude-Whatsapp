

# ClinicAI - Agente de Triagem via Chat

Este projeto implementa um agente de inteligência artificial para **triagens clínicas iniciais**.  
Ele recebe mensagens de usuários, conduz a conversa com ajuda de um modelo de linguagem (LLM) e armazena as interações em banco de dados MongoDB.

---

## 🎯 Objetivo

O agente tem como missão **coletar informações estruturadas** em um tom empático e profissional, garantindo segurança e ética no processo.  
As informações coletadas são:

- **Queixa principal** (motivo do contato)  
- **Sintomas detalhados**  
- **Duração e frequência**  
- **Intensidade (escala de 0 a 10)**  
- **Histórico relevante**  
- **Medidas já tomadas**  

⚠️ **O agente não substitui um profissional de saúde.**  
Ele não fornece diagnósticos nem tratamentos, apenas agiliza a coleta de dados.  
Mensagens com termos de emergência disparam alerta imediato, orientando o usuário a procurar socorro (ex.: “dor no peito”, “falta de ar”, “desmaio”).

---


## 🏗️ Arquitetura


clinicai-whatsapp-agent/
├─ app/
│  ├─ main.py              # App FastAPI
│  ├─ routes/              # Rotas REST (webhook, healthcheck)
│  ├─ services/            # Integração com WhatsApp, LLM, Mongo
│  ├─ schemas/             # Modelos Pydantic
│  ├─ agents/              # Persona e regras
│  ├─ prompts/             # Arquivos de prompt
│  ├─ constants/           # Emergências, intents
│  └─ utils/               # Logging, hashing, etc.
├─ tests/                  # Testes unitários e de integração
├─ scripts/                # Scripts auxiliares (webhook, túnel)
├─ .env.example            # Exemplo de variáveis de ambiente
├─ pyproject.toml          # Dependências (Poetry)
└─ README.md



---

## ⚙️ Configuração

### 1. Variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:



Edite os valores necessários.
📌 **Você deve preencher manualmente**:

* `MONGO_URI` → URL do seu MongoDB local ou em nuvem.
* `MONGO_DB` → Nome do banco.
* `GOOGLE_API_KEY` → Chave da API Gemini (console Google AI Studio).
* `APP_SECRET` e `HASH_SALT` → strings aleatórias para segurança.

Os campos relacionados ao WhatsApp podem ser configurados depois, caso queira integração real.

---

### 2. Instalação

Ative o ambiente virtual e instale as dependências:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
poetry install
```

---

### 3. Executar a API

Inicie o servidor:

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

A API ficará disponível em:
👉 [http://localhost:8000](http://localhost:8000)

Rotas úteis:

* `/health` → healthcheck
* `/webhook/whatsapp` → entrada de mensagens

---

### 4. Testes

Execute toda a suíte de testes:

```bash
poetry run pytest -v
```

---

## 🚑 Fluxo de Emergência

Se o usuário enviar mensagens com palavras-chave críticas (ex.: "dor no peito", "falta de ar", "desmaio"), a resposta automática será:

```
Entendi. Seus sintomas podem indicar uma situação de emergência. 
Por favor, procure o pronto-socorro mais próximo ou ligue para o 192 imediatamente.
```

Esse comportamento está centralizado em `app/constants/emergencies.py`.

---

## 📦 Alternativa de Frontend

Caso a API do WhatsApp não esteja disponível, este backend pode ser integrado a uma interface de chat que simula a experiência de mensagens instantâneas.
Cada conversa iniciada nessa interface começa com contexto zerado, assim como no WhatsApp.

---

## ✅ Checklist de Funcionamento

* [ ] Criou e configurou `.env` (com ao menos `MONGO_URI`, `MONGO_DB`, `GOOGLE_API_KEY`, `APP_SECRET`, `HASH_SALT`)
* [ ] Instalou dependências com `poetry install`
* [ ] Subiu o backend com `uvicorn`
* [ ] Rodou `pytest -v` e todos os testes passaram

---

## 📌 Autor

**Gustavo Diego**
📧 [gustavodiego298@gmail.com](mailto:gustavodiego298@gmail.com)

Se encontrar problemas ou quiser sugerir melhorias, pode **abrir uma issue** neste repositório.
