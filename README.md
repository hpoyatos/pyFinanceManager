# 🚀 pyFinanceManager

Um sistema de gestão financeira pessoal moderno, construído com **Python** e **Flask**, focado em automação, inteligência de dados e uma experiência visual premium (**Glassmorphism**).

---

## ✨ Funcionalidades Principais

### 📊 Dashboard Inteligente
- **Gráfico de Pizza Dinâmico:** Visualização de despesas agrupadas por **Categoria Pai**.
- **Herança de Inteligência:** Se uma transação não tem categoria, o sistema herda automaticamente a categoria do estabelecimento associado.
- **Gráficos Comparativos:** Orçado vs Realizado mensal.

### 🏦 Gestão de Contas e Lançamentos
- **Filtro por Conta:** Navegação focada por banco ou cartão, evitando confusão de dados.
- **Paginação de Alta Performance:** Carregamento de 30 em 30 itens para fluidez total.
- **Observações Detalhadas:** Suporte a textos longos (tipo TEXT) para descritivos de notas fiscais ou listas de compras.

### 🏢 Inteligência de Estabelecimentos
- **Aprendizado por Sinônimos:** O motor OFX aprende nomes curtos/confusos de faturas e associa aos estabelecimentos corretos.
- **Borracha Mágica (Fusão):** Ferramenta para fundir estabelecimentos duplicados, movendo transações e sinônimos automaticamente.
- **Geolocalização (IBGE):** Vinculação de Estado e Município via API oficial do IBGE para análise geográfica de gastos.

### 📁 Gestão de Documentos (Anexos N)
- **Múltiplos Anexos:** Suporte a N arquivos por transação.
- **Leitura Inteligente (PDF/XML):** 
    - Reconhece **DANFE/NF-e** automaticamente.
    - Detecta faturas de **Luz, Água e Internet** lendo o conteúdo do PDF e atribuindo ícones dinâmicos.
    - Suporte a leitura de arquivos **XML** nativos.

### 📥 Importador OFX Ultra-Seguro
- **Prevenção de Duplicidade:** Utiliza o FITID bancário para garantir que nenhuma transação seja importada duas vezes, mesmo em arquivos complementares.
- **Classificação Automática:** Detecta transferências, PIX e pagamentos de fatura sem poluir o cadastro de estabelecimentos.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.x + Flask
- **Banco de Dados:** SQLAlchemy ORM (Configurado para MariaDB/MySQL)
- **Frontend:** HTML5, CSS Nativo (Glassmorphism Design System), FontAwesome 6
- **Bibliotecas:** `pypdf` (OCR/Parsing), `ofxparse`, `python-dotenv`.

---

## 🚀 Como Rodar o Projeto

### 1. Pré-requisitos
Certifique-se de ter o Python instalado e um servidor **MariaDB** ou **MySQL** ativo.

### 2. Configuração do ambiente
```bash
# Clone o repositório
git clone <url-do-repo>

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto seguindo o modelo:
```env
SQLALCHEMY_DATABASE_URI=mysql+pymysql://USUARIO:SENHA@192.168.15.254:3306/pyfinance
SECRET_KEY=sua_chave_secreta_aqui
```

### 4. Execução
```bash
# Inicie a aplicação
python run.py
```
Acesse em seu navegador: `http://localhost:5000`

---

## 📝 Notas de Versão
As transações bancárias do tipo **Cartão de Crédito** são tratadas com prioridade na tela de Faturas, onde o sistema separa o que é gasto mensal da conta corrente das compras parceladas do cartão.
