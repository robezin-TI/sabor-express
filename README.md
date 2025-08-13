# 🚚 Rota Inteligente: Otimização de Entregas com IA

## 📌 Descrição do Problema
A empresa fictícia **Sabor Express** enfrenta desafios para otimizar suas entregas,
especialmente em horários de pico. Atualmente, as rotas são definidas manualmente,
resultando em atrasos e maiores custos.

Este projeto aplica **algoritmos de Inteligência Artificial** para sugerir as melhores
rotas de entrega, reduzindo tempo e custos.

---

## 🎯 Objetivos
- Criar um sistema capaz de calcular **rotas otimizadas** entre múltiplos pontos.
- Agrupar entregas próximas usando **K-Means**.
- Utilizar **A*** para calcular o menor caminho entre pontos no grafo.
- Fornecer uma visualização das rotas e tempos estimados.

---

## 🛠 Tecnologias Utilizadas
- **Python 3**
- [NetworkX](https://networkx.org/)
- [Scikit-learn](https://scikit-learn.org/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Plotly](https://plotly.com/)
- [Flask](https://flask.palletsprojects.com/)

---

## 🚀 Como Executar
```bash
# 1. Clonar repositório
git clone https://github.com/seu-usuario/rota-inteligente.git
cd rota-inteligente

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar projeto
python src/main.py
