"""
Main Triage Engine
Coordinates Rule Engine + ML Model for 95% Accuracy
"""
import os
import pickle
from typing import Dict, Optional, Any, List
from .rule_engine import SeverityRuleEngine, DepartmentRuleEngine, DeptResult
from .multilingual import ExplanationTemplates

class MedicalTriageEngine:
    """
    High-accuracy medical triage system
    Hybrid approach: Rules (precision) + ML (recall)
    """
    
    AVAILABLE_DEPTS = {
        "Cardiology", "Gastroenterology", "ENT", "Gynecology",
        "General Medicine", "Neurology", "Pediatrics", "Dermatology",
        "Emergency Medicine", "Orthopedics"
    }
    
    _instance = None

    def __init__(self, model_path: Optional[str] = None):
        self.severity_engine = SeverityRuleEngine()
        self.dept_engine = DepartmentRuleEngine()
        self.explanation_gen = ExplanationTemplates()
        
        # Load ML model if exists
        self.ml_model = None
        self.ml_vectorizer = None
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "models",
                "doctor_recommender.pkl"
            )
        self._load_ml_model(model_path)

    @classmethod
    def get_instance(cls) -> "MedicalTriageEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_ml_model(self, model_path: str):
        """Load trained ML model"""
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.ml_model = data.get('model')
                    self.ml_vectorizer = data.get('vectorizer')
            except Exception as e:
                print(f"Warning: Could not load ML model: {e}")
    
    def analyze(self, symptoms: str, age: Optional[int] = None, gender: Optional[str] = None) -> Dict[str, Any]:
        """
        Main triage analysis function
        
        Returns strict JSON format:
        {
            "medical_category": str,
            "severity": "LOW"|"MEDIUM"|"HIGH",
            "assigned_doctor": str,
            "room_allotted": str,
            "status": "ASSIGNED"|"REFER",
            "explainability": {...}
        }
        """
        # 1. Determine Severity (Rule-based - mandatory)
        severity = self.severity_engine.determine_severity(symptoms, age)

        # 2. Determine Department (Hybrid: Rules + ML)
        dept_result: DeptResult = self.dept_engine.classify_department(symptoms, age, gender)
        
        # Store original keywords from rule engine
        original_keywords = dept_result.get('keywords', [])
        
        # 4. ML Override if low confidence from rules
        if dept_result.get("method") != "refer_rule" and dept_result['confidence'] < 0.6 and self.ml_model:
            ml_dept = self._ml_predict(symptoms)
            if ml_dept and ml_dept != dept_result['department']:
                dept_result = {
                    "department": ml_dept,
                    "confidence": 0.75,  # Default ML confidence
                    "keywords": original_keywords + ["ml_predicted"],  # Preserve original + add ML marker
                    "method": "ml_override"
                }
            elif not dept_result.get('keywords'):
                # Ensure keywords exist even for low confidence rule matches
                dept_result['keywords'] = original_keywords if original_keywords else ["ml_predicted"]
        
        # 5. Check availability
        final_dept = dept_result.get('department')
        if final_dept and self.dept_engine.is_available(final_dept):
            status = "ASSIGNED"
            room = self._allocate_room(severity)
        else:
            # REFER case
            status = "REFER"
            final_dept = None
            room = "None"
        
        # 6. Generate explanations
        keywords = dept_result.get('keywords', [])
        explanations = self.explanation_gen.get_explanation(
            final_dept or "REFER",
            severity,
            keywords
        )
        
        return {
            "medical_category": final_dept or "REFER",
            "severity": severity,
            "assigned_doctor": final_dept if status == "ASSIGNED" else "None",
            "room_allotted": room,
            "status": status,
            "explainability": {
                "key_keywords": keywords[:5],
                "explanation_en": explanations['en'],
                "explanation_kn": explanations['kn'],
                "explanation_hi": explanations['hi']
            }
        }
    
    def _ml_predict(self, text: str) -> Optional[str]:
        """Get prediction from ML model"""
        if not self.ml_model or not self.ml_vectorizer:
            return None
        
        try:
            X = self.ml_vectorizer.transform([text])
            pred = self.ml_model.predict(X)[0]
            return pred if pred in self.AVAILABLE_DEPTS else None
        except Exception:
            return None
    
    def _allocate_room(self, severity: str) -> str:
        """Allocate room based on severity"""
        if severity == "HIGH":
            return "Emergency / ICU"
        elif severity == "MEDIUM":
            return "General Ward"
        else:
            return "Outpatient / No Room"
    
    def batch_analyze(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple cases"""
        return [self.analyze(c['symptoms'], c.get('age'), c.get('gender')) for c in cases]

# Singleton instance for import
triage_engine = MedicalTriageEngine.get_instance()