# Browser demo for the ML PII guard

This example spins up a tiny FastAPI application that lets you paste text in the browser and preview what the `MLPIIDetectorGuard` flags as personally identifiable information (PII).

## Prerequisites

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[demo]'
```

The first time you run the demo the Hugging Face model weights (`dslim/bert-base-NER` by default) will be downloaded to your local cache.

## Running the server

```bash
uvicorn examples.browser_demo.app:app --reload
```

Then open <http://127.0.0.1:8000> in your browser and paste some text. The guard will display whether the input is allowed, warn-only, or blocked and show the detected PII entities.

### Customising the model

Use environment variables to change the deployed model or detection threshold.

```bash
export PII_MODEL_NAME=ml6team/bert-base-NER
export PII_THRESHOLD=0.8
uvicorn examples.browser_demo.app:app --reload
```

Any model compatible with the Hugging Face `pipeline("ner")` API can be used, including locally fine-tuned checkpoints.
