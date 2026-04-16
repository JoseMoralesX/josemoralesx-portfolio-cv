from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.ml_model import load_model

# Initialize FastAPI App
app = FastAPI(
    title="Legal AI Text Classifier",
    description="An AI-powered API to classify legal documents into Contract, Litigation, or Compliance categories.",
    version="1.0.0"
)

# Load ML Model at startup
model = load_model()

class DocumentRequest(BaseModel):
    text: str

class ClassificationResponse(BaseModel):
    category: str
    confidence: float

@app.get("/")
def health_check():
    """Health check endpoint for AWS Load Balancer/ECS"""
    return {"status": "healthy", "service": "legal-ai-classifier"}

@app.post("/predict", response_model=ClassificationResponse)
def predict_category(doc: DocumentRequest):
    """
    Predicts the category of a legal document snippet.
    """
    if not doc.text or len(doc.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    # Predict probabilities
    probs = model.predict_proba([doc.text])[0]
    classes = model.classes_
    
    # Find the most likely class
    max_prob_index = probs.argmax()
    predicted_class = classes[max_prob_index]
    confidence = probs[max_prob_index]
    
    return ClassificationResponse(
        category=predicted_class,
        confidence=round(confidence, 4)
    )
