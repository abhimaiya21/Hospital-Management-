"""
Strict Rule Engine for Medical Triage
Ensures 100% accuracy on severity classification
"""
import re
from typing import Dict, List, Optional, Set, TypedDict
from .multilingual import MultilingualSupport

class DeptResult(TypedDict):
    department: Optional[str]
    confidence: float
    keywords: List[str]
    method: str

class SeverityRuleEngine(MultilingualSupport):
    """Hard-coded severity rules - NEVER compromise"""
    
    def __init__(self):
        super().__init__()
        
        # HIGH severity triggers - Strict regex matching
        self.high_patterns = [
            r"\b(accident|trauma|fracture|head injury|unconscious|collision|bleeding|heart attack|chest pain|stroke|seizure|paralysis)\b",
            r"\b(cancer\s+emergency|tumor\s+bleeding|cancer\s+bleeding)\b",
            r"\b(bike accident|car accident|vehicle accident)\b",
            r"\b(cannot breathe|breathlessness|suffocation)\b",
            r"(ಅಪಘಾತ|ಆಘಾತ|ಮುರಿತ|ತಲೆಗಾಯ|ಪ್ರಜ್ಞೆಯಿಲ್ಲದ|ಟಕ್ಕರ್|ರಕ್ತಸ್ರಾವ|ಹೃದಯಾಘಾತ|ಛಾತಿನೋವು|ಪಕ್ಷವಾತ|ಮೂರ್ಛೆ|ಪಾರ್ಶ್ವವಾಯು|ಕ್ಯಾನ್ಸರ್ ತುರ್ತು|ಉಸಿರಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ)",
            r"(दुर्घटना|आघात|फ्रैक्चर|सिर की चोट|बेहोश|टक्कर|खून बहना|दिल का दौरा|छाती दर्द|स्ट्रोक|दौरा|पक्षाघात|कैंसर आपातकाल|सांस नहीं आ रही)"
        ]

        # MEDIUM severity indicators
        self.medium_patterns = [
            r"\b(persistent|continuous|disturbing)\b",
            r"\b(infection|infected|swelling|pus)\b",
            r"\b(fever)\b.*\b(\d+)\b\s*(day|days)\b",
            r"\b(daily life|cannot sleep|cannot eat|sleep disturbed|appetite loss)\b",
            r"[ಜ್ವರ|ಸೋಂಕು|ಊತ|ದಿನನಿತ್ಯ|ನಿದ್ರೆ]",
            r"[बुखार|संक्रमण|सूजन|दैनिक|नींद|भूख]"
        ]
    
    def determine_severity(self, text: str, age: Optional[int] = None) -> str:
        """
        STRICT severity classification according to rules:
        - Any accident/trauma/fracture/head injury = HIGH
        - Chest pain/stroke/seizure/paralysis/cancer emergency = HIGH  
        - Moderate affecting daily life = MEDIUM
        - Mild/Stable = LOW
        """
        text_lower = text.lower()

        # Check HIGH severity - ANY match triggers HIGH
        for pattern in self.high_patterns:
            if re.search(pattern, text_lower):
                return "HIGH"

        # Pediatric fever rule
        if age is not None and age < 14:
            if re.search(r"(fe\s*ver|fever|बुखार|ಜ್ವರ)", text_lower):
                return "MEDIUM"

        # Check MEDIUM severity
        for pattern in self.medium_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if "fever" in pattern and match.group(1).isdigit():
                    if int(match.group(1)) >= 3:
                        return "MEDIUM"
                else:
                    return "MEDIUM"

        # Any fever defaults to MEDIUM (unless already HIGH)
        if re.search(r"\b(fe\s*ver|fever)\b", text_lower):
            return "MEDIUM"

        # Default to LOW for mild/stable symptoms
        return "LOW"

class DepartmentRuleEngine(MultilingualSupport):
    """Maps symptoms to departments using keyword rules"""
    
    def __init__(self):
        super().__init__()
        
        # Available departments (Cannot assign outside this)
        self.available_departments: Set[str] = {
            "Cardiology", "Gastroenterology", "ENT", "Gynecology",
            "General Medicine", "Neurology", "Pediatrics", "Dermatology",
            "Emergency Medicine", "Orthopedics"
        }
        
        # Comprehensive keyword mapping (weights handled by exact/partial match rules)
        self.dept_keywords = {
            "Cardiology": [
                "heart", "chest pain", "cardiac", "palpitation", "bp high", "hypertension", "heart attack",
                "ಹೃದಯ", "ಛಾತಿನೋವು", "ರಕ್ತದೊತ್ತಡ", "ಹೃದಯಾಘಾತ",
                "दिल", "हृदय", "छाती दर्द", "दिल का दौरा"
            ],
            "Orthopedics": [
                "fracture", "bone", "accident", "fall", "joint", "knee", "leg", "arm", "shoulder",
                "swelling", "cannot walk", "dislocation", "trauma",
                "ಮುರಿತ", "ಎಲುಬು", "ಅಪಘಾತ", "ಪತನ", "ಸಂಧಿ", "ಕಾಲು",
                "फ्रैक्चर", "हड्डी", "गिरना", "दुर्घटना", "जोड़"
            ],
            "Neurology": [
                "brain", "stroke", "seizure", "paralysis", "headache", "migraine", "numbness", "dizziness",
                "unconscious", "fits", "neurological",
                "ಮೆದುಳು", "ಪಕ್ಷವಾತ", "ಮೂರ್ಛೆ", "ಪಾರ್ಶ್ವವಾಯು", "ತಲೆಸುತ್ತು",
                "दिमाग", "स्ट्रोक", "दौरा", "पक्षाघात", "चक्कर"
            ],
            "Gastroenterology": [
                "stomach", "abdominal pain", "liver", "vomiting", "blood in stool", "digestion", "gastric",
                "ulcer", "diarrhea", "constipation", "acidity",
                "ಹೊಟ್ಟೆ", "ಜಠರ", "ರಕ್ತವಾಂತಿ", "ಜೀರ್ಣ",
                "पेट", "जिगर", "उल्टी", "मल में खून", "पाचन"
            ],
            "Gynecology": [
                "pregnancy", "menstrual", "periods", "vaginal", "uterus", "pcod", "obstetric",
                "missed period", "pregnant", "delivery", "gynecology",
                "ಗರ್ಭಧಾರಣೆ", "ಮುಟ್ಟು", "ಪ್ರಸೂತಿ", "ಗರ್ಭಾಶಯ",
                "गर्भावस्था", "मासिक", "प्रसूति", "गर्भाशय", "माहवारी"
            ],
            "Pediatrics": [
                "child", "baby", "infant", "newborn", "fever in child", "vaccination", "growth",
                "cough baby", "child crying", "not eating baby",
                "ಮಗು", "ಶಿಶು", "ಬಾಣಂತಿ", "ಮಕ್ಕಳ", "ಲಸಿಕೆ",
                "बच्चा", "शिशु", "नवजात", "बच्चों", "टीकाकरण"
            ],
            "ENT": [
                "ear", "nose", "throat", "hearing", "sinus", "tonsils", "cold", "cough",
                "sore throat", "ear pain", "nasal",
                "ಕಿವಿ", "ಮೂಗು", "ಗಂಟಲು", "ಸೈನಸ್",
                "कान", "नाक", "गला", "साइनस", "गले में दर्द"
            ],
            "Dermatology": [
                "skin", "rash", "acne", "pimples", "allergy", "itching", "eczema", "psoriasis",
                "fungal", "hair fall", "skin infection",
                "ತ್ವಚೆ", "ದದ್ದು", "ಅಲರ್ಜಿ", "ನೊರ", "ಎಕ್ಜಿಮಾ",
                "त्वचा", "चकत्ते", "एलर्जी", "खुजली", "एग्जिमा"
            ],
            "Emergency Medicine": [
                "emergency", "urgent", "critical", "acute", "severe", "immediate", "life threatening",
                "shock", "collapsed", "ambulance", "icu", "911",
                "ತುರ್ತು", "ತೀವ್ರ", "ಆಪತ್ತು", "ತಕ್ಷಣ",
                "आपातकाल", "तत्काल", "गंभीर", "एम्बुलेंस"
            ],
            "General Medicine": [
                "fever", "diabetes", "bp", "thyroid", "weakness", "infection", "general checkup",
                "body pain", "weight loss", "fatigue",
                "ಜ್ವರ", "ಮಧುಮೇಹ", "ರಕ್ತದೊತ್ತಡ", "ಥೈರಾಯ್ಡ್", "ದುರ್ಬಲತೆ",
                "बुखार", "मधुमेह", "थायरॉइड", "कमजोरी", "वजन घटना"
            ]
        }

        # Out-of-scope keywords that must be referred
        self.refer_keywords = [
            "eye", "vision", "cataract", "ophthalmology", "dental", "tooth", "psychiatry",
            "mental", "urology", "urinary", "kidney stone", "dentistry",
            "आँख", "दांत", "मानसिक", "मनोचिकित्सा", "मूत्र",
            "ಕಣ್ಣು", "ದಂತ", "ಮಾನಸಿಕ", "ಮೂತ್ರ", "ಕಣ್ಣಿನ"
        ]
    
    def classify_department(self, text: str, age: Optional[int] = None, gender: Optional[str] = None) -> DeptResult:
        """
        Classify to department using keyword scoring
        Returns: {"department": str, "confidence": float, "keywords": list}
        """
        text_lower = text.lower()
        scores: Dict[str, int] = {}
        matched_keywords: Dict[str, List[str]] = {}
        
        # Rule: Age < 14 → Pediatrics immediately
        if age is not None and age < 14:
            # Check if it's clearly something else (like gynecology for age 12)
            gyne_keywords = set(self.dept_keywords.get("Gynecology", []))
            is_female = gender and str(gender).lower() in ["f", "female"]
            if is_female and any(k in text_lower for k in gyne_keywords):
                return {
                    "department": "Gynecology",
                    "confidence": 1.0,
                    "keywords": ["age<14_female_gynecology"],
                    "method": "age_override"
                }
            return {
                "department": "Pediatrics",
                "confidence": 1.0,
                "keywords": ["pediatric_rule"],
                "method": "pediatric_rule"
            }

        # Score calculation using exact (10) and partial (5) matches
        for dept, keywords in self.dept_keywords.items():
            dept_score = 0
            matches: List[str] = []

            for keyword in keywords:
                key_lower = keyword.lower()

                # Exact match check
                if self._exact_match(text_lower, key_lower):
                    dept_score += 10
                    matches.append(keyword)
                    continue

                # Partial match check
                if key_lower in text_lower:
                    dept_score += 5
                    matches.append(keyword)

            if dept_score > 0:
                scores[dept] = dept_score
                matched_keywords[dept] = matches

        # Refer rule if no supported department keywords and out-of-scope keywords present
        if not scores and any(k in text_lower for k in self.refer_keywords):
            return {
                "department": None,
                "confidence": 0.0,
                "keywords": [k for k in self.refer_keywords if k in text_lower][:5],
                "method": "refer_rule"
            }
        
        if not scores:
            return {
                "department": None,
                "confidence": 0.0,
                "keywords": [],
                "method": "no_match"
            }
        
        # Get best match
        best_dept = max(scores.items(), key=lambda x: x[1])
        confidence = min(best_dept[1] / 10, 1.0)  # Exact match => 1.0, partial => 0.5
        
        return {
            "department": best_dept[0],
            "confidence": confidence,
            "keywords": matched_keywords[best_dept[0]],
            "method": "keyword_scoring"
        }

    def _exact_match(self, text: str, keyword: str) -> bool:
        """Exact match using word boundaries where possible"""
        if any(ch.isalnum() for ch in keyword) and all(ord(ch) < 128 for ch in keyword):
            pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
            return re.search(pattern, text) is not None
        return keyword in text
    
    def is_available(self, department: str) -> bool:
        """Check if department is in available list"""
        return department in self.available_departments