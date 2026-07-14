# 📈 Dashboard de Valuation: Graham & Bazin (B3)

Um web app interativo desenvolvido em **Python** e **Streamlit** para extração e análise automatizada de indicadores fundamentalistas de ações da bolsa brasileira (B3). 

Este projeto foi desenvolvido para demonstrar a aplicação prática da engenharia de software na análise financeira fundamentalista. Ele automatiza o processo de coleta de dados contábeis e aplica diretamente duas das metodologias clássicas de precificação de ativos, servindo como uma ferramenta ágil para *screening* de investimentos.

## 🚀 Funcionalidades

* **Pipeline de Extração Direta:** Web scraping nativo via `pandas` e `requests` no portal Fundamentus, garantindo controle total sobre os dados extraídos sem depender de bibliotecas de terceiros desatualizadas.
* **Fórmula de Graham:** Cálculo automático do Valor Patrimonial por Ação (VPA), Lucro por Ação (LPA) e Preço Justo, com tratamento de exceções matemáticas (filtrando empresas com prejuízo ou patrimônio líquido negativo).
* **Fórmula de Bazin:** Projeção estruturada do Preço Teto baseada na premissa de um *Dividend Yield* alvo de 6% ao ano.
* **Filtros Dinâmicos e UI/UX:** Interface intuitiva em barra lateral para parametrizar ativos por Liquidez Diária e Margens de Segurança mínimas.
* **Tabelas Otimizadas:** Visualização de dados interativa (nativa do Streamlit) com ordenação correta e formatação em escala real (R$) e percentuais (%).

## 🛠️ Tecnologias Utilizadas

* **Python 3:** Linguagem base para lógica e cálculos matemáticos.
* **Streamlit:** Construção rápida do frontend interativo.
* **Pandas:** Estruturação em DataFrames, limpeza e tipagem de dados extraídos de tabelas HTML.
* **NumPy:** Vetorização de cálculos e tratamento de divisões por zero (`np.nan`).

## ⚙️ Como executar o projeto localmente

1. **Clone este repositório:**
   ```bash
   git clone https://github.com/jr-quant/fundamentalista.git
   cd valuation-dashboard
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows use: .venv\Scripts\activate
   ```

3. **Instale as dependências rigorosas:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação:**
   ```bash
   streamlit run app.py
   ```

5. O painel ficará disponível no seu navegador através do endereço genérico `http://localhost:8501`.

## ⚠️ Aviso Legal

Este projeto tem fins estritamente **educacionais** e de demonstração de arquitetura de dados aplicados ao mercado financeiro. Os cálculos gerados por esta ferramenta são baseados em dados públicos não auditados pelo autor e **não constituem recomendação de compra, venda ou manutenção de ativos financeiros.**