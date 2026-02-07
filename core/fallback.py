def fallback_message(lang="en"):
    messages = {
        "en": "Unable to identify condition clearly. Please consult a doctor.",
        "hi": "स्थिति स्पष्ट नहीं है। कृपया डॉक्टर से संपर्क करें।",
        "te": "స్థితి స్పష్టంగా గుర్తించలేకపోయాము. దయచేసి వైద్యుడిని సంప్రదించండి."
    }
    return messages[lang]
