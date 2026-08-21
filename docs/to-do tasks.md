Com base nos documentos `PROJECT_PLAN.md` e `functional-specification.md`, elaborei um guia de desenvolvimento detalhado, estruturado como uma **To-Do List complexa e sequencial**. Este roteiro cobre desde a infraestrutura até os testes finais, detalhando as rotas de API, o schema do banco de dados e os formulários do frontend.

---

# 🚀 Open Body Tracker: Guia de Desenvolvimento Passo a Passo

## 🏗️ Fase 1: Infraestrutura e Configuração Inicial
- [ ] **1.1. Inicializar o Repositório**
  - [ ] Criar estrutura de pastas: `/backend`, `/frontend`, `/docs`, `/docker`.
  - [ ] Configurar `.gitignore` (ignorando `.env`, `node_modules`, `__pycache__`, volumes do docker).
- [ ] **1.2. Configurar Docker Compose (`docker-compose.yml`)**
  - [ ] Serviço `db`: PostgreSQL 15 (com variáveis de ambiente para user/pass/db e volume persistente `pgdata`).
  - [ ] Serviço `backend`: Python 3.11+ (FastAPI), mapeando porta 8000 e volume de código.
  - [ ] Serviço `frontend`: Node 20+ (Vite/React), mapeando porta 3000.
  - [ ] Serviço `storage`: Volume mapeado para upload de fotos (`/app/storage/photos`).
- [ ] **1.3. Configurar Variáveis de Ambiente (`.env`)**
  - [ ] Definir `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM` (para JWT), `CORS_ORIGINS`.

---

## 🗄️ Fase 2: Schema do Banco de Dados (Backend)
*Foco: Integridade de dados, suporte a i18n e conversão de unidades.*

- [ ] **2.1. Criar Modelos SQLAlchemy (ou Prisma)**
  - [ ] `User`: `id` (UUID), `email` (unique), `hashed_password`, `full_name`, `birth_date`, `biological_sex`, `default_unit_system` (enum: METRIC, IMPERIAL), `created_at`.
  - [ ] `MetricCode` (Catálogo): `id`, `key` (ex: `weight`, `bicep_circumference`), `category` (vitals, circumference, skinfold, performance), `is_bilateral` (boolean).
  - [ ] `UnitCode`: `id`, `key` (ex: `kg`, `cm`, `mm`, `lbs`, `in`), `system_type` (METRIC, IMPERIAL), `conversion_factor_to_base` (float).
  - [ ] `Assessment`: `id`, `user_id` (FK), `assessment_date`, `notes`, `protocol_used` (FK opcional), `created_at`.
  - [ ] `Measurement`: `id`, `assessment_id` (FK), `metric_code_id` (FK), `unit_code_id` (FK), `value_raw` (float - *sempre salvo na unidade base do sistema, ex: kg/cm/mm*), `side` (enum: RIGHT, LEFT, NONE).
  - [ ] `SkinfoldProtocol`: `id`, `name` (ex: "Jackson-Pollock 7-site"), `formula_key`, `required_sites` (JSON/Array).
  - [ ] `Photo`: `id`, `assessment_id` (FK), `file_path`, `angle` (enum: FRONT, SIDE, BACK), `uploaded_at`.
- [ ] **2.2. Seeders (Dados Iniciais)**
  - [ ] Inserir `MetricCode` (todos os campos de circunferência, dobras, vitais).
  - [ ] Inserir `UnitCode` (kg, g, cm, mm, m, lbs, oz, in, ft).
  - [ ] Inserir `SkinfoldProtocol` (Focar no MVP: **Jackson & Pollock 7-site**).

---

## 🧠 Fase 3: Lógica de Negócio e Motor de Cálculo (Backend)
- [ ] **3.1. Camada de Conversão de Unidades**
  - [ ] Criar serviço `UnitConverter`: Função para converter qualquer entrada do usuário para a unidade base do sistema (Métrico) antes de salvar no DB.
  - [ ] Implementar lógica de round-trip (Imperial -> Métrico -> Imperial) para exibição no frontend sem perda de precisão.
- [ ] **3.2. Motor de Cálculo de Composição Corporal**
  - [ ] Implementar fórmula de **Densidade Corporal** para Jackson-Pollock 7-site (Pectoral, Axillary, Tricipital, Subscapular, Abdominal, Suprailiac, Thigh).
  - [ ] Implementar fórmula de **Siri/Brozek** para converter Densidade Corporal em **Body Fat %**.
  - [ ] Criar funções para calcular: **BMI** (Peso/Altura²), **WHR** (Cintura/Quadril), **Média Bilateral** (ex: média do braço D+E) e **Assimetria** (%).
- [ ] **3.3. Motor de Milestones (Marcos)**
  - [ ] Criar lógica para comparar a avaliação atual com o histórico e gerar "badges" (ex: "Menor Gordura Corporal", "Perdeu 5kg", "Recorde de Prancha").

---

## 🔌 Fase 4: Rotas de API e Contratos de Dados (FastAPI)
*Autenticação via JWT. Todas as rotas (exceto auth) devem validar o `user_id` do token.*

- [ ] **4.1. Autenticação e Perfil**
  - [ ] `POST /api/v1/auth/register`: Cria usuário, hasheia senha (bcrypt/argon2).
  - [ ] `POST /api/v1/auth/login`: Valida e retorna `access_token` (JWT).
  - [ ] `GET /api/v1/user/profile`: Retorna dados estáticos do usuário.
  - [ ] `PUT /api/v1/user/profile`: Atualiza dados estáticos (nome, altura, preferências).
- [ ] **4.2. Avaliações (O Contrato Crítico)**
  - [ ] `POST /api/v1/assessments/new`:
    - *Payload*: `assessment_date`, `measurements` (array de `{metric_key, value, unit, side}`), `photos` (multipart/form-data).
    - *Ação*: Converte unidades, salva no DB, calcula métricas derivadas (BMI, BF%), detecta milestones.
  - [ ] `GET /api/v1/assessments/history`:
    - *Query Params*: `start_date`, `end_date`, `metric_filter`.
    - *Ação*: Retorna série temporal otimizada para gráficos (carregamento < 2s).
  - [ ] `GET /api/v1/assessments/{id}`: Retorna detalhes completos de uma avaliação (incluindo URLs das fotos).
  - [ ] `POST /api/v1/assessments/import`:
    - *Payload*: CSV file.
    - *Ação*: Valida cabeçalhos, converte dados, faz preview, commit transacional.
- [ ] **4.3. Portabilidade de Dados**
  - [ ] `GET /api/v1/data/export`: Gera e faz stream de um CSV com todo o histórico do usuário.
  - [ ] `GET /api/v1/metrics/catalog`: Retorna o catálogo de métricas e unidades (para popular dropdowns no frontend).

---

## 🎨 Fase 5: Fundação do Frontend (React + TS)
- [ ] **5.1. Setup Inicial**
  - [ ] Iniciar projeto com Vite + React + TypeScript.
  - [ ] Instalar TailwindCSS, Headless UI (Radix), Recharts, React Hook Form + Zod (validação), `react-i18next`, Axios.
- [ ] **5.2. Estrutura de Estado e Rotas**
  - [ ] Configurar React Router (`/login`, `/dashboard`, `/assessments/new`, `/analytics`, `/settings`).
  - [ ] Criar `AuthContext` (gerenciamento de token JWT, interceptors do Axios).
  - [ ] Configurar `i18n` (carregar `en.json` e `pt.json` do diretório `/locales`).
- [ ] **5.3. Componentes Base (Design System)**
  - [ ] Criar `<Button>`, `<Input>`, `<Select>`, `<Card>`, `<Modal>` usando Headless UI + Tailwind.
  - [ ] Criar componente `<UnitToggle>` (Switch global entre Métrico/Imperial que altera a exibição localmente).

---

## 📝 Fase 6: Formulários do Frontend (Detalhamento)
*O coração da aplicação. Devem ser acessíveis, validados em tempo real e suportar i18n.*

### 📋 Formulário 1: Onboarding / Perfil do Usuário
- [ ] **Campos:**
  - `full_name` (Texto, obrigatório)
  - `birth_date` (Date picker, obrigatório - usado para calcular idade)
  - `biological_sex` (Radio: Male/Female - obrigatório para fórmulas de gordura)
  - `height_cm` (Numérico, obrigatório - usado para BMI)
  - `default_unit_system` (Toggle: Métrico/Imperial)
  - `consent_accepted` (Checkbox com texto legal LGPD/GDPR)
- [ ] **Validação:** Idade > 10 e < 120; Altura > 50cm e < 250cm.

### 📋 Formulário 2: Assistente de Nova Avaliação (Assessment Wizard)
*Dividido em 5 passos (Stepper). Usa `react-hook-form` com estado persistente entre passos.*

- [ ] **Passo 1: Dados Gerais e Vitais**
  - `weight` (Numérico + seletor de unidade kg/lbs)
  - `resting_heart_rate` (Numérico, bpm)
  - `blood_pressure` (Dois inputs: Sistólica / Diastólica)
  - *Cálculo em tempo real*: Exibir BMI assim que peso e altura (do perfil) estiverem presentes.
- [ ] **Passo 2: Circunferências (Perimetria)**
  - *Layout*: Grid responsivo. Para cada medida, input de valor + toggle Lado (D/E ou Único).
  - *Campos*: Peito, Cintura, Quadril, Abdômen, Braço D/E (relaxado e contraído), Antebraço D/E, Coxa D/E, Panturrilha D/E.
  - *Cálculo em tempo real*: Exibir WHR (Cintura/Quadril) e Assimetria (ex: "Braço D 2% maior que E").
- [ ] **Passo 3: Dobras Cutâneas (Adipometria)**
  - *Seletor de Protocolo*: Dropdown (MVP: Jackson & Pollock 7-site).
  - *Campos Dinâmicos*: O formulário renderiza os 7 campos exatos exigidos pelo protocolo (Peitoral, Axilar, Tricipital, Subescapular, Abdominal, Suprailíaca, Coxa).
  - *Unidade*: Fixa em milímetros (mm).
  - *Cálculo em tempo real*: Exibir "Gordura Corporal: X% (Calc. via J&P 7)", "Massa Gorda: Y kg", "Massa Magra: Z kg".
- [ ] **Passo 4: Performance Física**
  - `abdominal_reps` (Numérico, repetições em 1 min)
  - `plank_duration` (Numérico, segundos)
- [ ] **Passo 5: Fotos e Revisão**
  - *Upload de Fotos*: 3 áreas de dropzone (Frente, Lado, Costas). Preview das imagens.
  - *Resumo*: Tabela com todas as métricas inseridas e os cálculos derivados.
  - *Ações*: "Salvar Rascunho" ou "Finalizar e Salvar".

### 📋 Formulário 3: Importação de CSV
- [ ] **Área de Upload**: Drag & drop para arquivo `.csv`.
- [ ] **Tela de Preview**: Tabela mostrando as primeiras 5 linhas.
- [ ] **Mapeamento**: Dropdowns em cada cabeçalho do CSV para mapear para as `MetricKeys` do sistema.
- [ ] **Validação Visual**: Linhas com erro (ex: texto onde deveria ter número) ficam vermelhas.
- [ ] **Botão**: "Confirmar Importação" (dispara `POST /api/v1/assessments/import`).

---

## 📊 Fase 7: Analytics e Visualização (Frontend)
- [ ] **7.1. Dashboard (Home)**
  - [ ] Cards de "Última Avaliação" (Peso, BF%, BMI).
  - [ ] Gráfico de linha simples (Recharts) mostrando tendência de peso dos últimos 3 meses.
  - [ ] Lista de "Alertas" (ex: "Avaliação atrasada", "Nova meta atingida").
- [ ] **7.2. Módulo de Tendências (Time-Series)**
  - [ ] Seletor de Métrica (Dropdown com todas as `MetricKeys`).
  - [ ] Seletor de Período (Date Range Picker).
  - [ ] Gráfico de Linha Interativo (Recharts): Suporte a zoom, tooltip customizado mostrando valor na unidade preferida do usuário.
  - [ ] Toggle para "Média Móvel" (ex: média de 3 avaliações).
- [ ] **7.3. Motor de Comparação e Milestones**
  - [ ] *Comparison View*: Dropdown para selecionar "Avaliação A" e "Avaliação B". Tabela lado a lado mostrando Valor A, Valor B, Variação Absoluta e Variação % (com setas verdes/vermelhas).
  - [ ] *Milestones View*: Galeria de "Badges" conquistados (ex: Ícone de troféu para "Menor Peso da História").
- [ ] **7.4. Timeline de Fotos**
  - [ ] Grid de fotos ordenado por data.
  - [ ] *Before/After Slider*: Componente que sobrepõe a foto mais antiga e a mais recente, permitindo arrastar uma barra para comparar a evolução física.

---

## 🧪 Fase 8: Testes e Garantia de Qualidade (QA)
- [ ] **8.1. Testes Unitários (Backend - Pytest)**
  - [ ] Testar `UnitConverter`: Garantir que 10 lbs -> kg -> lbs retorna exatamente 10 lbs (precisão decimal).
  - [ ] Testar `SkinfoldEngine`: Inserir medidas fixas do Jackson-Pollock 7 e assertar o % de Gordura exato contra uma calculadora científica de referência.
  - [ ] Testar `BMICalculator` e `WHRCalculator`.
- [ ] **8.2. Testes de Integração (Backend - TestClient)**
  - [ ] Testar fluxo de `POST /assessments/new`: Verificar se o banco cria o `Assessment`, os `Measurements` e as `Photos` transacionalmente.
  - [ ] Testar `POST /assessments/import` com CSV corrompido: Assertar que a API retorna HTTP 400 com mensagens de erro detalhadas e **não** corrompe o banco.
- [ ] **8.3. Testes E2E (Frontend - Playwright/Cypress)**
  - [ ] *Jornada 1*: Login -> Preencher Perfil -> Criar Avaliação 1 -> Criar Avaliação 2 -> Verificar gráfico de tendência.
  - [ ] *Segurança*: Tentar acessar `/api/v1/assessments/history` com o token do Usuário B e assertar que retorna 403/401 ou lista vazia (Data Isolation).
  - [ ] *Milestone*: Criar dados que simulem uma perda de 5kg e verificar se o badge de milestone aparece na UI.

---

## 🚀 Fase 9: Polish, Acessibilidade e Deploy
- [ ] **9.1. Acessibilidade (WCAG 2.1 AA)**
  - [ ] Garantir que todos os formulários têm `<label>` associados.
  - [ ] Garantir que os gráficos do Recharts tenham tabelas ocultas (screen-reader only) com os dados brutos.
  - [ ] Verificar contraste de cores (especialmente nos gráficos de tendência verde/vermelho).
- [ ] **9.2. Otimização de Performance**
  - [ ] Implementar paginação ou "infinite scroll" no histórico de avaliações se > 50 registros.
  - [ ] Adicionar cache no frontend para o `MetricCatalog` (não buscar do backend toda hora).
- [ ] **9.3. Documentação e Release**
  - [ ] Escrever `README.md` com instruções de `docker compose up -d`.
  - [ ] Criar `docs/csv-template.csv` para download.
  - [ ] Configurar Webhooks do Weblate (se aplicável) para o repositório de traduções.
  - [ ] Taggear versão `v1.0.0` no Git.