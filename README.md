# AICoverGen - AI Voice Cover Generator

Transform any song into AI-generated covers using Retrieval-based Voice Conversion (RVC)!

## Features
- Vocal separation (MDX-Net)
- Voice conversion (RVC models)
- Pitch control, reverb, mixing
- Gradio Web UI

## Quick Start
git clone https://github.com/abhinav01050/AICoverGen.git
cd AICoverGen
python -m venv .venv
source .venv/bin/activate # Linux/Mac

or .venv\Scripts\activate # Windows
pip install -r requirements.txt
python src/webui1.py


Open `http://127.0.0.1:7860`
