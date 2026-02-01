"""
Multilingual support for Kannada (kn), Hindi (hi), and English (en)
95% Accuracy Medical Triage System
"""

import re
from typing import Dict, Tuple, List, Optional

class MultilingualSupport:
    def __init__(self):
        # Severity patterns in all 3 languages
        self.high_severity_patterns = {
            'en': r'\b(accident|trauma|fracture|head injury|unconscious|collision|bleeding|heart attack|chest pain|stroke|seizure|paralysis|cancer emergency|attack|severe pain|cannot breathe|fall|injury)\b',
            'kn': r'\b(ಅಪಘಾತ|ಆಘಾತ|ಮುರಿತ|ತಲೆಗಾಯ|ಪ್ರಜ್ಞೆಯಿಲ್ಲದ|ಟಕ್ಕರ್|ರಕ್ತಸ್ರಾವ|ಹೃದಯಾಘಾತ|ಛಾತಿನೋವು|ಪಕ್ಷವಾತ|ಮೂರ್ಛೆ|ಪಾರ್ಶ್ವವಾಯು|ಕ್ಯಾನ್ಸರ್ ತುರ್ತು|ದಾಳಿ|ತೀವ್ರ ನೋವು|ಉಸಿರಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ|ಪತನ|ಗಾಯ)\b',
            'hi': r'\b(दुर्घटना|आघात|फ्रैक्चर|सिर की चोट|बेहोश|टक्कर|खून बहना|दिल का दौरा|छाती दर्द|स्ट्रोक|दौरा|पक्षाघात|कैंसर आपातकाल|हमला|गंभीर दर्द|सांस नहीं ले सकता|गिरावट|चोट)\b'
        }
        
        self.medium_severity_patterns = {
            'en': r'\b(moderate|persistent|continuous|disturbing|fever.*days|infection|swelling|daily life|sleep|appetite)\b',
            'kn': r'\b(ಮ Mitt|ನಿರಂತರ|ತೊಂದರೆ|ಜ್ವರ.*ದಿನಗಳು|ಹೆಚ್ಚು ಸೋಂಕು|ಊತ|ದಿನನಿತ್ಯ|ನಿದ್ರೆ|ಆಹಾರ)\b',
            'hi': r'\b(मध्यम|लगातार|परेशान करने वाला|बुखार.*दिन|संक्रमण|सूजन|दैनिक जीवन|नींद|भूख)\b'
        }
        
        # Department translations for output
        self.dept_translations = {
            "Cardiology": {"en": "Cardiology", "kn": "ಹೃದಯರೋಗ ವಿಭಾಗ", "hi": "हृदय रोग विभाग"},
            "Gastroenterology": {"en": "Gastroenterology", "kn": "ಜೀರ್ಣಾಂಗ ರೋಗ ವಿಭಾಗ", "hi": "गैस्ट्रोएंटरोलॉजी विभाग"},
            "ENT": {"en": "ENT", "kn": "ಕಿವಿ-ಮೂಗು-ಗಂಟಲು ವಿಭಾಗ", "hi": "कान-नाक-गला विभाग"},
            "Gynecology": {"en": "Gynecology", "kn": "ಪ್ರಸೂತಿ ಮತ್ತು ಸ್ತ್ರೀರೋಗ ವಿಭಾಗ", "hi": "प्रसूति एवं स्त्री रोग विभाग"},
            "General Medicine": {"en": "General Medicine", "kn": "ಸಾಮಾನ್ಯ ವೈದ್ಯಕೀಯ ವಿಭಾಗ", "hi": "सामान्य चिकित्सा विभाग"},
            "Neurology": {"en": "Neurology", "kn": "ನರವಿಜ್ಞಾನ ವಿಭಾಗ", "hi": "न्यूरोलॉजी विभाग"},
            "Pediatrics": {"en": "Pediatrics", "kn": "ಮಕ್ಕಳ ವೈದ್ಯಕೀಯ ವಿಭಾಗ", "hi": "बाल रोग विभाग"},
            "Dermatology": {"en": "Dermatology", "kn": "ಚರ್ಮರೋಗ ವಿಭಾಗ", "hi": "त्वचा रोग विभाग"},
            "Oncology": {"en": "Oncology", "kn": "ಕ್ಯಾನ್ಸರ್ ಚಿಕಿತ್ಸಾ ವಿಭಾಗ", "hi": "कैंसर रोग विभाग"},
            "Emergency Medicine": {"en": "Emergency Medicine", "kn": "ತುರ್ತು ವೈದ್ಯಕೀಯ ವಿಭಾಗ", "hi": "आपातकालीन चिकित्सा विभाग"},
            "Orthopedics": {"en": "Orthopedics", "kn": "ಅಸ್ಥಿ ಮತ್ತು ಸಂಧಿ ರೋಗ ವಿಭಾಗ", "hi": "अस्थि एवं जोड़ रोग विभाग"}
        }

class ExplanationTemplates:
    """Tri-lingual explanation templates for each department"""
    
    def __init__(self):
        self.templates = {
            "Orthopedics": {
                "causes": {
                    "en": "Traumatic injury with suspected bone fracture or joint dislocation detected",
                    "kn": "ಆಘಾತದ ಗಾಯ ಮತ್ತು ಮುರಿತ (ಮುರಿತ) ಅಥವಾ ಸಂಧಿ ತಪ್ಪಿರುವ ಸಾಧ್ಯತೆ ಪತ್ತೆಯಾಯಿತು",
                    "hi": "आघात चोट में फ्रैक्चर या जोड़ उतरने की संभावना"
                },
                "severity_high": {
                    "en": "Rule #2: Any accident/trauma/fracture requires HIGH severity emergency protocol",
                    "kn": "ನಿಯಮ #2: ಯಾವುದೇ ಅಪಘಾತ/ಆಘಾತ/ಮುರಿತವು HIGH ಗಂಭೀರತೆಯ ತುರ್ತು ಪ್ರೋಟೋಕಾಲ್ ಅಗತ್ಯ",
                    "hi": "नियम #2: कोई भी दुर्घटना/आघात/फ्रैक्चर HIGH गंभीरता आपातकालीन प्रोटोकॉल मांगता है"
                }
            },
            "Cardiology": {
                "causes": {
                    "en": "Cardiovascular symptoms suggesting possible cardiac ischemia or arrhythmia",
                    "kn": "ಹೃದಯ ಅಲ್ಪರಕ್ತ ಪೂರೈಕೆ ಅಥವಾ ಅನിയಮಿತ ಬಡಿತದ ಸಾಧ್ಯತೆಯಿರುವ ಹೃದಯ ಸಂಬಂಧಿತ ಲಕ್ಷಣಗಳು",
                    "hi": "हृदय रक्ताभाव या अनियमित धड़कन की संभावना वाले हृदय संबंधी लक्षण"
                },
                "severity_high": {
                    "en": "Rule: Chest pain and cardiac symptoms require HIGH severity assessment",
                    "kn": "ನಿಯಮ: ಛಾತಿನೋವು ಮತ್ತು ಹೃದಯದ ಲಕ್ಷಣಗಳು HIGH ಗಂಭೀರತೆ ಮೌಲ್ಯಮಾಪನ ಅಗತ್ಯ",
                    "hi": "नियम: छाती दर्द और हृदय लक्षण HIGH गंभीरता मूल्यांकन मांगते हैं"
                }
            },
            "Neurology": {
                "causes": {
                    "en": "Neurological deficits indicating possible stroke, seizure, or nerve damage",
                    "kn": "ಪಕ್ಷವಾತ, ಮೂರ್ಛೆ ಅಥವಾ ನರ ಹಾನಿಯ ಸಾಧ್ಯತೆಯಿರುವ ನರವೈಜ್ಞಾನಿಕ ಕೊರತೆಗಳು",
                    "hi": "स्ट्रोक, दौरा या नर्व क्षति की संभावना वाले न्यूरोलॉजिकल कमजोरियां"
                },
                "severity_high": {
                    "en": "Rule: Stroke symptoms, seizures, paralysis are HIGH severity time-critical",
                    "kn": "ನಿಯಮ: ಪಕ್ಷವಾತ ಲಕ್ಷಣಗಳು, ಮೂರ್ಛೆ, ಪಾರ್ಶ್ವವಾಯು HIGH ಗಂಭೀರತೆಯ ಟೈಮ್-ಕ್ರಿಟಿಕಲ್",
                    "hi": "नियम: स्ट्रोक लक्षण, दौरे, पक्षाघात HIGH गंभीरता टाइम-क्रिटिकल हैं"
                }
            },
            "Gastroenterology": {
                "causes": {
                    "en": "Gastrointestinal dysfunction with abdominal pathology",
                    "kn": "ಉದರ ಸಮಸ್ಯೆಗಳೊಂದಿಗೆ ಜೀರ್ಣಾಂಗ ದೋಷಗಳ ಸೂಚನೆ",
                    "hi": "पेट संबंधी विकृति के साथ गैस्ट्रोइंटेस्टाइनल समस्या"
                },
                "severity_high": {
                    "en": "Rule: Vomiting blood or severe abdominal pain indicates HIGH severity",
                    "kn": "ನಿಯಮ: ರಕ್ತವಾಂತಿಯ ಉದರದ ತೀವ್ರ ನೋವು HIGH ಗಂಭೀರತೆಯನ್ನು ಸೂಚಿಸುತ್ತದೆ",
                    "hi": "नियम: खून की उल्टी या गंभीर पेट दर्द HIGH गंभीरता दर्शाता है"
                }
            },
            "Gynecology": {
                "causes": {
                    "en": "Reproductive system symptoms requiring obstetric/gynecological evaluation",
                    "kn": "ಪ್ರಸೂತಿ/ಸ್ತ್ರೀರೋಗಶಾಸ್ತ್ರದ ಮೌಲ್ಯಮಾಪನದ ಅಗತ್ಯವಿರುವ ಪ್ರಜನನ ವ್ಯವಸ್ಥೆಯ ಲಕ್ಷಣಗಳು",
                    "hi": "प्रसूति/स्त्री रोग मूल्यांकन की आवश्यकता वाली प्रजनन तंत्र लक्षण"
                },
                "severity_high": {
                    "en": "Rule: Pregnancy complications or severe bleeding require HIGH severity",
                    "kn": "ನಿಯಮ: ಗರ್ಭಧಾರಣೆಯ ಸಮಸ್ಯೆಗಳು ಅಥವಾ ತೀವ್ರ ರಕ್ತಸ್ರಾವ HIGH ಗಂಭೀರತೆ ಅಗತ್ಯ",
                    "hi": "नियम: गर्भावस्था जटिलताएं या गंभीर रक्तस्राव HIGH गंभीरता मांगते हैं"
                }
            },
            "Pediatrics": {
                "causes": {
                    "en": "Pediatric patient (age <14) with age-specific medical condition",
                    "kn": "ಮಕ್ಕಳ ರೋಗಿ (ವಯಸ್ಸು <14) ವಯಸ್ಸು-ನಿರ್ದಿಷ್ಟ ವೈದ್ಯಕೀಯ ಸ್ಥಿತಿಯೊಂದಿಗೆ",
                    "hi": "बाल रोगी (उम्र <14) उम्र-विशिष्ट चिकित्सा स्थिति के साथ"
                },
                "severity_high": {
                    "en": "Rule: Children with trauma/fever/severe symptoms require HIGH severity",
                    "kn": "ನಿಯಮ: ಪೆಠೋಲೋಗಿ/ಜ್ವರ/ತೀವ್ರ ಲಕ್ಷಣಗಳಿರುವ ಮಕ್ಕಳಿಗೆ HIGH ಗಂಭೀರತೆ ಅಗತ್ಯ",
                    "hi": "नियम: आघात/बुखार/गंभीर लक्षण वाले बच्चों को HIGH गंभीरता चाहिए"
                }
            },
            "ENT": {
                "causes": {
                    "en": "Otorhinolaryngology symptoms affecting ear, nose, or throat",
                    "kn": "ಕಿವಿ, ಮೂಗು ಅಥವಾ ಗಂಟಲನ್ನು ಪ್ರಭಾವಿಸುವ ಓಟೋರೈನೋಲೇರಿಂಗೋಲಾಜಿ ಲಕ್ಷಣಗಳು",
                    "hi": "कान, नाक या गले को प्रभावित करने वाले ओटोराइनोलैरिंगोलॉजी लक्षण"
                },
                "severity_high": {
                    "en": "Rule: Severe airway obstruction or bleeding requires HIGH severity",
                    "kn": "ನಿಯಮ: ತೀವ್ರ ಉಸಿರಾಟದ ಅವರೋಧ ಅಥವಾ ರಕ್ತಸ್ರಾವ HIGH ಗಂಭೀರತೆ ಅಗತ್ಯ",
                    "hi": "नियम: गंभीर सांस रोक या खून बहना HIGH गंभीरता मांगता है"
                }
            },
            "Dermatology": {
                "causes": {
                    "en": "Dermatological condition involving skin, hair, or nails",
                    "kn": "ತ್ವಚೆ, ಕೇಶ ಅಥವಾ ಉಗುರುಗಳನ್ನು ಒಳಗೊಂಡಿರುವ ಚರ್ಮವಿಜ್ಞಾನ ಸ್ಥಿತಿ",
                    "hi": "त्वचा, बाल या नाखून को शामिल करने वाली त्वचा रोग स्थिति"
                },
                "severity_high": {
                    "en": "Rule: Severe allergic reactions or infections require HIGH severity",
                    "kn": "ನಿಯಮ: ತೀವ್ರ ಅಲರ್ಜಿ ಪ್ರತಿಕ್ರಿಯೆಗಳು ಅಥವಾ ಸೋಂಕುಗಳು HIGH ಗಂಭೀರತೆ ಅಗತ್ಯ",
                    "hi": "नियम: गंभीर एलर्जी प्रतिक्रिया या संक्रमण HIGH गंभीरता मांगते हैं"
                }
            },
            "Oncology": {
                "causes": {
                    "en": "Oncological symptoms suggesting cancer or tumor pathology",
                    "kn": "ಕ್ಯಾನ್ಸರ್ ಅಥವಾ ಟ್ಯೂಮರ್ ಪ್ಯಾಥಾಲಜಿಯನ್ನು ಸೂಚಿಸುವ ಆನ್ಕೊಲಾಜಿಕಲ್ ಲಕ್ಷಣಗಳು",
                    "hi": "कैंसर या ट्यूमर विकृति का संकेत देने वाले ऑन्कोलॉजिकल लक्षण"
                },
                "severity_high": {
                    "en": "Rule: Cancer emergencies (severe pain, bleeding) require HIGH severity",
                    "kn": "ನಿಯಮ: ಕ್ಯಾನ್ಸರ್ ತುರ್ತುಗಳು (ತೀವ್ರ ನೋವು, ರಕ್ತಸ್ರಾವ) HIGH ಗಂಭೀರತೆ ಅಗತ್ಯ",
                    "hi": "नियम: कैंसर आपातकाल (गंभीर दर्द, खून बहना) HIGH गंभीरता मांगते हैं"
                }
            },
            "Emergency Medicine": {
                "causes": {
                    "en": "Critical emergency requiring immediate medical intervention",
                    "kn": "ತ್ವರಿತ ವೈದ್ಯಕೀಯ ಹಸ್ತಕ್ಷೇಪದ ಅಗತ್ಯವಿರುವ ತೀವ್ರ ತುರ್ತು",
                    "hi": "तत्काल चिकित्सा हस्तक्षेप की आवश्यकता वाली गंभीर आपातकाल"
                },
                "severity_high": {
                    "en": "Rule: All emergency cases are HIGH severity by definition",
                    "kn": "ನಿಯಮ: ಎಲ್ಲಾ ತುರ್ತು ಪ್ರಕರಣಗಳು ವ್ಯಾಖ್ಯಾನದ ಪ್ರಕಾರ HIGH ಗಂಭೀರತೆ",
                    "hi": "नियम: सभी आपातकालीन मामले परिभाषा के अनुसार HIGH गंभीरता हैं"
                }
            },
            "General Medicine": {
                "causes": {
                    "en": "General internal medicine symptoms (fever, diabetes, hypertension)",
                    "kn": "ಸಾಮಾನ್ಯ ಆಂತರಿಕ ವೈದ್ಯಕೀಯ ಲಕ್ಷಣಗಳು (ಜ್ವರ, ಮಧುಮೇಹ, ರಕ್ತದೊತ್ತಡ)",
                    "hi": "सामान्य आंतरिक चिकित्सा लक्षण (बुखार, मधुमेह, उच्च रक्तचाप)"
                },
                "severity_high": {
                    "en": "Rule: Very high fever (>103F) or diabetic emergencies require HIGH severity",
                    "kn": "ನಿಯಮ: ಬಹಳ ಜ್ವರ (>103F) ಅಥವಾ ಮಧುಮೇಹ ತುರ್ತುಗಳು HIGH ಗಂಭೀರತೆ ಅಗತ್ಯ",
                    "hi": "नियम: बहुत अधिक बुखार (>103F) या मधुमेह आपातकाल HIGH गंभीरता मांगते हैं"
                }
            },
            "REFER": {
                "causes": {
                    "en": "Specialized care not available in current hospital",
                    "kn": "ಸ್ಥಿತಿಗಾಗಿ ಪ್ರಸ್ತುತ ಆಸ್ಪತ್ರೆಯಲ್ಲಿ ಲಭ್ಯವಿಲ್ಲದ ವಿಶೇಷ ವಿಭಾಗದ ಅಗತ್ಯವಿದೆ",
                    "hi": "इस स्थिति के लिए वर्तमान अस्पताल में उपलब्ध नहीं विशेष विभाग की आवश्यकता"
                },
                "severity_high": {
                    "en": "Cannot assess severity - specialist unavailable",
                    "kn": "ಗಂಭೀರತೆಯನ್ನು ಮೌಲ್ಯಮಾಪನ ಮಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ - ತಜ್ಞ ಲಭ್ಯವಿಲ್ಲ",
                    "hi": "गंभीरता का मूल्यांकन नहीं कर सकते - विशेषज्ञ उपलब्ध नहीं"
                }
            }
        }
    
    def get_explanation(self, dept: str, severity: str, keywords: Optional[List[str]] = None) -> Dict[str, str]:
        """Generate tri-lingual explanation"""
        keywords = keywords or []
        template = self.templates.get(dept, self.templates["General Medicine"])
        
        # Base cause explanation
        explanations = {
            "en": template["causes"]["en"],
            "kn": template["causes"]["kn"],
            "hi": template["causes"]["hi"]
        }
        
        # Add severity reasoning
        if severity == "HIGH":
            explanations["en"] += f". {template['severity_high']['en']}"
            explanations["kn"] += f". {template['severity_high']['kn']}"
            explanations["hi"] += f". {template['severity_high']['hi']}"
        elif severity == "MEDIUM":
            med_text = " Moderate symptoms affecting daily activities require observation."
            med_kn = " ದಿನನಿತ್ಯದ ಚಟುವಟಿಕೆಗಳನ್ನು ಪ್ರಭಾವಿಸುವ ಮಧ್ಯಮ ಲಕ್ಷಣಗಳಿಗೆ ನಿಗಾ ಅಗತ್ಯ."
            med_hi = " दैनिक गतिविधियों को प्रभावित करने वाले मध्यम लक्षणों के लिए निगरानी आवश्यक।"
            explanations["en"] += med_text
            explanations["kn"] += med_kn
            explanations["hi"] += med_hi
        
        # Add keywords
        if keywords:
            kw_str = ", ".join(keywords[:5])
            explanations["en"] += f" Detected indicators: {kw_str}."
            explanations["kn"] += f" ಪತ್ತೆಯಾದ ಸೂಚಕಗಳು: {kw_str}."
            explanations["hi"] += f" पहचाने गए संकेत: {kw_str}।"
        
        return explanations

def detect_language(text: str) -> Tuple[str, float]:
    """Detect if text contains Kannada or Hindi characters"""
    # Count Kannada characters (U+0C80–U+0CFF)
    kn_count = len(re.findall(r'[\u0C80-\u0CFF]', text))
    # Count Hindi characters (U+0900–U+097F)
    hi_count = len(re.findall(r'[\u0900-\u097F]', text))
    
    total_chars = len(text.strip())
    
    if kn_count > total_chars * 0.1:  # >10% Kannada
        return 'kn', kn_count / total_chars
    elif hi_count > total_chars * 0.1:  # >10% Hindi
        return 'hi', hi_count / total_chars
    else:
        return 'en', 1.0