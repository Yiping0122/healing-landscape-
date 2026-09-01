# Healing Landscape Digital Twin — Streamlit

An operator-facing research demonstrator that translates simulated physiological evidence into a multi-scale healing-environment intervention workflow.

The app presents one evolving twin state through seven views:

`Sense → Represent → Infer → Explain → Map → Review → Update`

## What the prototype demonstrates

- Adjustable physiological inputs: SDNN, BPM, QTc and LF/HF
- Five operational stress-state levels for interactive exploration
- Human, environmental, spatial, decision, intervention and feedback states
- Personal, room, building and landscape intervention scales
- Four genuine review outcomes: Approve, Modify, Escalate and Monitor Only
- Directional post-intervention transitions across Human, Environment and Twin State

## Scientific boundary

This is a research and conference demonstrator. It does **not** provide a clinical diagnosis, predict an individual treatment effect, actuate real building systems, or report measured recovery. Post-intervention outputs express directional system-state changes only.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository and upload the contents of this folder.
2. Open [share.streamlit.io](https://share.streamlit.io/).
3. Select the repository, branch, and `app.py` as the entry point.
4. Click **Deploy**. No secrets or external database are required.

## Suggested repository name

`healing-landscape-digital-twin`

## Project structure

```text
.
├── .streamlit/config.toml
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
```

