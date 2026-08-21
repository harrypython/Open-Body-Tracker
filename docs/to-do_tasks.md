Com base nos documentos `PROJECT_PLAN.md` e `functional-specification.md`, elaborei um guia de desenvolvimento detalhado, estruturado como uma **To-Do List complexa e sequencial**. Este roteiro cobre desde a infraestrutura até os testes finais, detalhando as rotas de API, o schema do banco de dados e os formulários do frontend.

---

# 🚀 Open Body Tracker: Guia de Desenvolvimento Passo a Passo (v1.1)

## 🏗️ Fase 1: Infraestrutura e Configuração Inicial ✅ *(CONCLUÍDA)*
- [x] **1.1. Inicializar o Repositório**
  - [x] Criar estrutura de pastas: `/backend`, `/frontend`, `/docs`, `/docker`.
  - [x] Configurar `.gitignore` (ignorando `.env`, `node_modules`, `__pycache__`, volumes do docker).
- [x] **1.2. Configurar Docker Compose (`docker-compose.yml`)**
  - [x] Serviço `db`: PostgreSQL 15 (com variáveis de ambiente para user/pass/db e volume persistente `pgdata`).
  - [x] Serviço `backend`: Python 3.11+ (FastAPI), mapeando porta 8000 e volume de código.
  - [x] Serviço `frontend`: Node 20+ (Vite/React), mapeando porta 3000.
  - [x] Serviço `storage`: Volume mapeado para upload de fotos (`/app/storage/photos`).
- [x] **1.3. Configurar Variáveis de Ambiente (`.env`)**
  - [x] Definir `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM` (para JWT), `CORS_ORIGINS`.

---

## 🗄️ Fase 2: Schema do Banco de Dados (Backend)
*Foco: Integridade de dados, suporte a i18n e conversão de unidades. O banco sempre armazena na unidade base (kg, cm, mm).*

- [x] **2.1. Criar Modelos SQLAlchemy (ou Prisma)**
  - [x] `User`: `id` (UUID), `email` (unique), `hashed_password`, `full_name`, `birth_date`, `biological_sex`, `height_cm`, `default_unit_system` (enum: METRIC, IMPERIAL), `created_at`.
  - [x] `MetricCode` (Catálogo): `id`, `key` (ex: `weight_kg`, `arm_right_cm`), `category` (vitals, circumference, skinfold), `is_bilateral` (boolean).
  - [x] `UnitCode`: `id`, `key` (ex: `kg`, `cm`, `mm`, `lbs`, `in`), `system_type` (METRIC, IMPERIAL), `conversion_factor_to_base` (float).
  - [x] `Assessment`: `id`, `user_id` (FK), `assessment_date`, `notes`, `protocol_used` (FK opcional), `created_at`.
  - [x] `Measurement`: `id`, `assessment_id` (FK), `metric_code_id` (FK), `unit_code_id` (FK), `value_raw` (float - *sempre na unidade base*), `side` (enum: RIGHT, LEFT, NONE).
  - [x] `SkinfoldProtocol`: `id`, `name` (ex: "Jackson-Pollock 7-site"), `formula_key`, `required_sites` (JSON/Array).
  - [x] `Photo`: `id`, `assessment_id` (FK), `file_path`, `angle` (enum: FRONT, SIDE, BACK), `uploaded_at`.
- [x] **2.2. Seeders (Dados Iniciais - Catálogo de 27 Métricas)**
  - [x] **Vitals:** `weight_kg`, `resting_hr_bpm`, `bp_systolic_mmhg`, `bp_diastolic_mmhg`.
  - [x] **Circumferences (cm):** `arm_right_cm`, `arm_left_cm`, `arm_right_contracted_cm`, `arm_left_contracted_cm`, `forearm_right_cm`, `forearm_left_cm`, `chest_cm`, `abdomen_cm`, `waist_cm`, `hip_cm`, `thigh_right_cm`, `thigh_left_cm`, `calf_right_cm`, `calf_left_cm`.
  - [x] **Skinfolds (mm):** `tricipital_mm`, `subscapular_mm`, `mid_axillary_mm`, `suprailiac_mm`, `pectoral_mm`, `abdominal_mm`, `thigh_skinfold_mm`, `bicipital_mm`.
  - [x] **Protocolo J&P 7:** Configurar o seeder para exigir as 7 dobras exatas: `pectoral`, `mid_axillary`, `tricipital`, `subscapular`, `abdominal`, `suprailiac`, `thigh_skinfold`.

---

## 🧠 Fase 3: Lógica de Negócio e Motor de Cálculo (Backend)
- [x] **3.1. Camada de Conversão de Unidades**
  - [x] Criar serviço `UnitConverter`: Converte qualquer entrada (ex: lbs, in) para a unidade base (kg, cm, mm) antes de salvar.
  - [x] Implementar lógica de round-trip para exibição no frontend sem perda de precisão decimal.
- [x] **3.2. Motor de Cálculo de Composição Corporal**
  - [x] Implementar fórmula de **Densidade Corporal** para Jackson-Pollock 7-site.
  - [x] Implementar fórmula de **Siri/Brozek** para converter Densidade em **Body Fat %**.
  - [x] Criar funções para calcular: **BMI** (Peso/Altura²), **WHR** (Cintura/Quadril), **Média Bilateral** e **Assimetria %** (ex: Braço D vs E).
- [x] **3.3. Motor de Milestones (Marcos)**
  - [x] Criar lógica para comparar a avaliação atual com o histórico e gerar "badges" (ex: "Menor Gordura Corporal", "Perdeu 5kg").

---

## 🔌 Fase 4: Rotas de API e Contratos de Dados (FastAPI)
*Autenticação via JWT. Todas as rotas validam o `user_id` do token para isolamento de dados.*

- [x] **4.1. Autenticação e Perfil**
  - [x] `POST /api/v1/auth/register`: Cria usuário, hasheia senha.
  - [x] `POST /api/v1/auth/login`: Valida e retorna `access_token` (JWT).
  - [x] `GET /api/v1/user/profile`: Retorna dados estáticos (incluindo altura para BMI).
  - [x] `PUT /api/v1/user/profile`: Atualiza dados estáticos.
- [x] **4.2. Avaliações (O Contrato Crítico)**
  - [x] `POST /api/v1/assessments/new`:
    - *Payload*: JSON estruturado (ver exemplo abaixo) + `photos` (multipart/form-data).
    - *Ação*: Converte unidades, valida as 7 dobras do J&P 7, salva no DB, calcula métricas derivadas.
  - [x] `GET /api/v1/assessments/history`: Retorna série temporal otimizada para gráficos (carregamento < 2s).
  - [x] `GET /api/v1/assessments/{id}`: Detalhes completos de uma avaliação.
  - [x] `POST /api/v1/assessments/import`: Upload de CSV, valida, faz preview e commit transacional.
- [x] **4.3. Portabilidade e Catálogo**
  - [x] `GET /api/v1/data/export`: Stream de CSV com todo o histórico.
  - [x] `GET /api/v1/metrics/catalog`: Retorna o catálogo de métricas e unidades para o frontend.

**Exemplo de Payload para `POST /api/v1/assessments/new`:**
```json
{
  "assessment_date": "2023-10-27",
  "vitals": { "weight": 75.5, "resting_hr": 62, "bp_systolic": 120, "bp_diastolic": 80 },
  "circumferences": {
    "arm_right": 34.5, "arm_left": 34.0, "arm_right_contracted": 36.0, "arm_left_contracted": 35.5,
    "forearm_right": 28.0, "forearm_left": 27.5, "chest": 98.0, "abdomen": 85.0, 
    "waist": 82.0, "hip": 96.0, "thigh_right": 58.0, "thigh_left": 57.5, 
    "calf_right": 38.0, "calf_left": 37.5
  },
  "skinfolds": {
    "pectoral": 12.0, "mid_axillary": 10.0, "tricipital": 15.0, "subscapular": 14.0,
    "abdominal": 20.0, "suprailiac": 11.0, "thigh": 22.0, "bicipital": 13.0
  },
  "protocol_used": "JACKSON_POLLOCK_7"
}
```

---

## 🎨 Fase 5: Fundação do Frontend (React + TS)
- [ ] **5.1. Setup Inicial**
  - [ ] Iniciar projeto com Vite + React + TypeScript.
  - [ ] Instalar TailwindCSS, Radix UI, Recharts, React Hook Form + Zod, `react-i18next`, Axios.
- [ ] **5.2. Estrutura de Estado e Rotas**
  - [ ] Configurar React Router (`/login`, `/dashboard`, `/assessments/new`, `/analytics`, `/settings`).
  - [ ] Criar `AuthContext` (gerenciamento de JWT, interceptors do Axios).
  - [ ] Configurar `i18n` (carregar `en.json` e `pt.json`).
- [ ] **5.3. Componentes Base (Design System)**
  - [ ] Criar `<Button>`, `<Input>`, `<Select>`, `<Card>`, `<Modal>`.
  - [ ] Criar componente `<UnitToggle>` (Switch global Métrico/Imperial que altera a exibição localmente).

---

## 📝 Fase 6: Formulários do Frontend (Detalhamento)
*O coração da aplicação. Validados em tempo real, suportam i18n e as 27 métricas.*

### 📋 Formulário 1: Onboarding / Perfil do Usuário
- [ ] **Campos:** `full_name`, `birth_date`, `biological_sex`, `height_cm`, `default_unit_system`, `consent_accepted`.
- [ ] **Validação:** Idade > 10; Altura > 50cm e < 250cm.

### 📋 Formulário 2: Assistente de Nova Avaliação (Assessment Wizard)
*Dividido em 4 passos. Usa `react-hook-form` com schema Zod aninhado.*

- [ ] **Passo 1: Dados Gerais e Vitais**
  - [ ] Data da Avaliação (Date picker).
  - [ ] **Peso Corporal**: Input + seletor de unidade (kg/lbs). *Exibe BMI em tempo real.*
  - [ ] **Frequência Cardíaca**: Input (bpm).
  - [ ] **Pressão Arterial**: Dois inputs (Sistólica / Diastólica) em mmHg.
- [ ] **Passo 2: Circunferências (Perimetria)**
  - [ ] **Membros Superiores (Pares)**: Braço D/E (Relaxado e Contraído), Antebraço D/E. *Exibe assimetria %.*
  - [ ] **Tronco (Únicos)**: Tórax, Abdômen, Cintura, Quadril. *Exibe WHR (Cintura/Quadril).*
  - [ ] **Membros Inferiores (Pares)**: Coxa D/E, Panturrilha D/E.
- [ ] **Passo 3: Dobras Cutâneas (Adipometria)**
  - [ ] **Seletor de Protocolo**: Dropdown (Padrão: Jackson & Pollock 7-site).
  - [ ] **Grid de Dobras (Fixo em mm)**: Peitoral, Axilar Média, Tricipital, Subescapular, Abdominal, Supra-ilíaca, Coxa (Obrigatórias para J&P 7). Bicipital (Opcional).
  - [ ] **Feedback em Tempo Real**: Card destacado com **Gordura Corporal %**, **Massa Gorda (kg)** e **Massa Magra (kg)** assim que as 7 dobras forem preenchidas.
- [ ] **Passo 4: Revisão, Fotos e Salvamento**
  - [ ] Tabela resumo com todas as 27 métricas.
  - [ ] Upload de 3 fotos (Frente, Lado, Costas).
  - [ ] Botões: "Salvar Rascunho" ou "Finalizar".

### 📋 Formulário 3: Importação de CSV
- [ ] Área de Drag & Drop, Tela de Preview (5 linhas), Mapeamento de colunas via Dropdowns, Validação visual (linhas com erro em vermelho).

---

## 📊 Fase 7: Analytics e Visualização (Frontend)
- [ ] **7.1. Dashboard (Home)**
  - [ ] Cards de "Última Avaliação" (Peso, BF%, BMI).
  - [ ] Gráfico de linha simples (Recharts) com tendência de peso dos últimos 3 meses.
- [ ] **7.2. Módulo de Tendências (Time-Series)**
  - [ ] Seletor de Métrica (Dropdown com as 27 chaves) e Seletor de Período.
  - [ ] Gráfico de Linha Interativo com zoom e tooltip na unidade preferida do usuário.
- [ ] **7.3. Motor de Comparação e Milestones**
  - [ ] *Comparison View*: Dropdown para selecionar Avaliação A e B. Tabela com Variação Absoluta e % (setas verdes/vermelhas).
  - [ ] *Milestones View*: Galeria de "Badges" (ex: "Menor Peso da História").
- [ ] **7.4. Timeline de Fotos**
  - [ ] Grid ordenado por data e componente *Before/After Slider* para sobrepor fotos.

---

## 🧪 Fase 8: Testes e Garantia de Qualidade (QA)
- [ ] **8.1. Testes Unitários (Backend - Pytest)**
  - [ ] **Skinfold Engine**: Inserir dobras fixas do J&P 7 (ex: Peitoral=12, Axilar=10, Tríceps=15, Subescapular=14, Abdômen=20, Suprailíaca=11, Coxa=22) e assertar o % de Gordura exato.
  - [ ] **Conversion Layer**: Testar round-trip (10 lbs -> kg -> lbs = 10 lbs).
  - [ ] **Calculated Metrics**: Testar fórmulas de BMI, WHR e Assimetria (ex: Braço D=35, E=34 -> 2.9% assimetria).
- [ ] **8.2. Testes de Integração (Backend - TestClient)**
  - [ ] **Assessment Flow**: `POST /assessments/new` com todas as 27 métricas. Verificar criação transacional de `Assessment`, `Measurements` e `Photos`.
  - [ ] **Validation**: Enviar `POST` com apenas 6 dobras cutâneas e protocolo J&P 7. Assertar `HTTP 400` com mensagem *"Missing required skinfold: thigh_skinfold_mm"*.
  - [ ] **CSV Import**: Upload de CSV corrompido. Assertar `HTTP 400` sem corromper o banco.
- [ ] **8.3. Testes E2E (Frontend - Playwright/Cypress)**
  - [ ] **Jornada Completa**: Login -> Preencher Perfil -> Criar Avaliação 1 (com as 27 métricas) -> Criar Avaliação 2 -> Verificar gráfico de tendência e cálculo de variação.
  - [ ] **Segurança**: Tentar acessar histórico com token de outro usuário e assertar bloqueio (Data Isolation).
  - [ ] **Milestone**: Simular perda de 5kg entre duas avaliações e verificar se o badge aparece na UI.

---

## 🚀 Fase 9: Polish, Acessibilidade e Deploy
- [ ] **9.1. Acessibilidade (WCAG 2.1 AA)**
  - [ ] Garantir `<label>` associados em todos os inputs do wizard.
  - [ ] Adicionar tabelas ocultas (screen-reader only) nos gráficos do Recharts.
  - [ ] Verificar contraste de cores (verde/vermelho nas variações).
- [ ] **9.2. Otimização de Performance**
  - [ ] Implementar paginação/infinite scroll no histórico se > 50 registros.
  - [ ] Adicionar cache no frontend para o `MetricCatalog`.
- [ ] **9.3. Documentação e Release**
  - [ ] Escrever `README.md` com instruções de `docker compose up -d`.
  - [ ] Criar `docs/csv-template.csv` para download.
  - [ ] Configurar Webhooks do Weblate para o repositório de traduções.
  - [ ] Taggear versão `v1.0.0` no Git.