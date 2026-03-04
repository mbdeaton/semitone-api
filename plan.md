# FastAPI + Fly.io Deployment Plan

## Goal
Expose the `semitone` Python package via a public API endpoint so users can request:

> "Give me the frequencies of the tones in the C major scale"

Deploy as a minimal microservice using FastAPI and Fly.io.

---

# 1. Package Preparation

### 1.1 Ensure `semitone` is on PyPI
- Confirm `semitone` installs cleanly:
  ```bash
  pip install semitone
  ```
- Verify expected usage in a Python REPL.

---

# 2. Create the API Project

### 2.1 Create project directory

```bash
mkdir semitone-api
cd semitone-api
python -m venv venv
source venv/bin/activate
```

### 2.2 Install dependencies

```bash
pip install fastapi uvicorn semitone
pip freeze > requirements.txt
```

---

# 3. Implement REST API

Create `main.py`:

```python
from fastapi import FastAPI
from semitone import get_scale_frequencies  # adjust to actual API

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/scale")
def scale(root: str, mode: str = "major"):
    frequencies = get_scale_frequencies(root=root, mode=mode)
    return {
        "root": root,
        "mode": mode,
        "frequencies": frequencies
    }
```

---

# 4. Test Locally

```bash
uvicorn main:app --reload
```

Test in browser:

```
http://localhost:8000/scale?root=C&mode=major
```

Verify JSON response.

---

# 5. Dockerize the Service

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

# 6. Install Fly.io CLI

```bash
curl -L https://fly.io/install.sh | sh
fly auth login
```

---

# 7. Initialize Fly App

From project directory:

```bash
fly launch
```

When prompted:
- Choose a unique app name
- Choose a region
- Skip database setup

Confirm generated `fly.toml`.

---

# 8. Deploy

```bash
fly deploy
```

After deployment, Fly will provide a URL:

```
https://your-app-name.fly.dev
```

---

# 9. Test Public Endpoint

Example request:

```
https://your-app-name.fly.dev/scale?root=C&mode=major
```

Expected result: JSON list of frequencies for the C major scale.

---

# 10. Optional Enhancements

- Add input validation
- Add error handling
- Add logging
- Add rate limiting
- Add GraphQL endpoint
- Add unit tests
- Add CI/CD via GitHub Actions

---

# End State

You now have:

- A public HTTPS endpoint
- A containerized FastAPI microservice
- Your `semitone` package exposed globally
- A minimal production-style deployment

