import logging
from transformers import pipeline, AutoTokenizer
import torch
import gc

logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        # We initialize models as None to save RAM on startup.
        # They are lazy-loaded only when needed!
        self.classifier = None
        self.summarizer = None
        self.tokenizer = None

    def tokenize_text(self, text: str):
        """Phase 13.1: Fundamental NLP Tokenization"""
        if self.tokenizer is None:
            # Using distilbert tokenizer (very lightweight)
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        
        tokens = self.tokenizer.tokenize(text)
        return tokens

    def classify_workflow(self, text: str) -> str:
        """Phase 13.3: BERT Workflow Classification"""
        if self.classifier is None:
            # Using distilbert for zero-shot classification (very light on RAM, perfect for i3 8GB)
            self.classifier = pipeline(
                "zero-shot-classification",
                model="typeform/distilbert-base-uncased-mnli",
                device=-1 # Force CPU
            )
        
        candidate_labels = ["BLOCKER", "DELAY", "ESCALATION", "APPROVAL", "DEPENDENCY", "STATUS_UPDATE", "RISK"]
        
        result = self.classifier(text, candidate_labels)
        
        # Free up memory if needed, but pipeline handles it well
        best_label = result['labels'][0]
        confidence = result['scores'][0]
        
        logger.info(f"NLP Classified: {best_label} (Confidence: {confidence:.2f})")
        return best_label

    def summarize_workflow(self, text: str) -> str:
        """Phase 13.6: Transformer-Based Summarization"""
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        
        if self.summarizer is None:
            # t5-small is tiny (240MB) and runs fast on i3 CPUs
            self.summarizer = AutoModelForSeq2SeqLM.from_pretrained("t5-small")
            
        if self.tokenizer is None:
             self.tokenizer = AutoTokenizer.from_pretrained("t5-small")
             
        # T5 expects prefix "summarize: "
        if not text.startswith("summarize: "):
            text = "summarize: " + text
            
        inputs = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
        summary_ids = self.summarizer.generate(inputs["input_ids"], max_new_tokens=50, min_length=10)
        
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
    def free_memory(self):
        """Helper to clear RAM so the laptop doesn't lag."""
        self.classifier = None
        self.summarizer = None
        self.tokenizer = None
        gc.collect()

# Singleton instance
nlp_service = NLPService()
