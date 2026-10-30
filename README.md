# NVIDIA-Nemotron AI Text Optimizer

A lightweight, scalable Python application built for the Nebius x NVIDIA Global AI Hackathon. This project connects to the powerful `nvidia/Llama-3-1-Nemotron-70B-Instruct` open-weight model hosted via the Nebius AI Cloud infrastructure to instantly refine raw text into professional, clear, and grammatically perfect copy.

## 🚀 Inspiration
In today's fast-paced digital environment, clear communication is crucial. We wanted to build a zero-friction, incredibly fast utility tool that leverages cutting-edge open-weight LLMs optimized on GPU clusters to turn casual notes, raw drafts, or broken phrases into structured, business-ready professional output.

## ⚙️ How It Works
The application uses Python to interface with the Nebius Token Factory / AI Cloud endpoint using an OpenAI-compliant syntax block. 
1. The user inputs their unedited text.
2. The payload specifies the `Llama-3-1-Nemotron-70B-Instruct` model along with a strict system instruction tuning payload.
3. The server instantly processes the request using NVIDIA architecture and prints out an optimized output.

## 🛠️ Built With
* **Python 3** - For core backend execution logic.
* **NVIDIA Open Weights** - Powered by the `Llama-3-1-Nemotron-70B-Instruct` model for high-fidelity text structure mapping.
* **Nebius AI Cloud API Engine** - To deliver lightning-fast response streams over cloud inference nodes.

## 📈 What We Learned
* How to quickly interface with open-weight models via remote cloud APIs.
* Designing specific system prompts to steer highly technical models toward everyday user text optimization tasks.
* Structuring clean, minimal codebases ready for containerized or serverless microservice deployments.

