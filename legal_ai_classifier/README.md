# Legal AI Text Classifier API

A lightweight, high-performance Machine Learning API designed to automatically classify legal document snippets into core categories: **Contract**, **Litigation**, and **Compliance**.

Built with an SRE-first approach, this project features a containerized architecture (Docker) and Infrastructure-as-Code (Terraform) for seamless deployment to AWS.

## 🚀 Features

*   **Machine Learning NLP:** Uses `scikit-learn` (TF-IDF + Naive Bayes) for fast and effective text classification.
*   **High-Performance API:** Built on `FastAPI` and `Uvicorn` for asynchronous, fast HTTP request handling.
*   **Dockerized:** Ready for any container orchestration platform (Kubernetes, AWS ECS, App Runner).
*   **Infrastructure as Code (IaC):** Includes `Terraform` configurations to provision AWS ECR and AWS App Runner.

## 🛠 Tech Stack

*   **Language:** Python 3.10
*   **Web Framework:** FastAPI
*   **Machine Learning:** Scikit-Learn, Pandas
*   **Infrastructure & DevOps:** Docker, Terraform, AWS (ECR, App Runner)

## 💻 Local Development

### 1. Run with Python (Virtual Environment)

```bash
# Clone the repo and navigate to the directory
cd legal_ai_classifier

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server (The ML model will be trained automatically on first run)
uvicorn app.main:app --reload
```

### 2. Run with Docker

```bash
# Build the Docker image
docker build -t legal-ai-classifier .

# Run the container
docker run -p 8000:8000 legal-ai-classifier
```

## 📡 API Usage

Once the server is running, visit the interactive Swagger UI at: `http://localhost:8000/docs`

**Endpoint:** `POST /predict`

**Request Body:**
```json
{
  "text": "The Company shall ensure all user data is processed in compliance with the General Data Protection Regulation (GDPR)."
}
```

**Response:**
```json
{
  "category": "Compliance",
  "confidence": 0.8943
}
```

## ☁️ Cloud Deployment (AWS)

This project includes Terraform scripts (`infrastructure/main.tf`) to deploy the containerized application to AWS.

1.  Authenticate with your AWS CLI.
2.  Navigate to the `infrastructure` folder.
3.  Run the following Terraform commands:

```bash
terraform init
terraform plan
terraform apply
```

This will automatically provision an **Amazon ECR** repository for the Docker image and an **AWS App Runner** service to serve the FastAPI application globally with auto-scaling enabled.

---
*Created as a demonstration of combining Data/ML Engineering with modern SRE and DevOps practices.*