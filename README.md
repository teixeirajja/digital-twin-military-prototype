# Digital Twin Militar — Protótipo Streamlit

Protótipo demonstrador para a cadeira de EITT.

## Objetivo

Mostrar, de forma simples, como uma plataforma de Digital Twin pode apoiar:

- militares no acompanhamento da sua evolução física;
- comandantes/treinadores na leitura da prontidão da unidade;
- simulação de treinos antes da execução;
- identificação de fadiga, risco de lesão e sobrecarga muscular.

## Estrutura da pasta

```text
digital_twin_prototipo/
├── app.py
├── requirements.txt
├── run_local.bat
├── run_server.sh
├── data/
│   ├── militares.csv
│   ├── registos_diarios.csv
│   ├── testes_fisicos.csv
│   └── lesoes.csv
├── utils/
│   ├── data_loader.py
│   ├── metrics.py
│   ├── simulator.py
│   └── styles.py
└── .streamlit/
    └── config.toml
```

## Como correr localmente no Windows

Dentro da pasta do projeto:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Ou clicar em `run_local.bat`.

## Como correr no servidor Linux

Depois de enviar a pasta para o servidor:

```bash
cd digital_twin_prototipo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Ou:

```bash
chmod +x run_server.sh
./run_server.sh
```

## Login de demonstração

A aplicação não tem autenticação real. O login é simulado através da escolha do perfil no topo da página.

Perfis disponíveis:

- Comandante: `Cap José Teixeira`
- Militares: restantes perfis da base de dados

## Dados

Os dados em `data/` são fictícios e servem apenas para demonstrar o MVP.
