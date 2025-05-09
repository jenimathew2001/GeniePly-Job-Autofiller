json_schema = {
    "title": "resume",
    "description": "Structured information extracted from a resume.",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Full name of the candidate",
            "default": "N/A"
        },
        "contact": {
            "type": "object",
            "description": "Contact details",
            "properties": {
                "email": {"type": "string", "description": "Email address", "default": "N/A"},
                "phone": {"type": "string", "description": "Phone number", "default": "N/A"},
                "location": {"type": "string", "description": "Current location", "default": "N/A"}
            }
        },
        "summary": {
            "type": "string",
            "description": "Professional summary",
            "default": "N/A"
        },
        
        "education": {
            "type": "array",
            "description": "List of educational qualifications",
            "items": {
                "type": "object",
                "properties": {
                    "degree": {"type": "string", "description": "Degree obtained", "default": "N/A"},
                    "institution": {"type": "string", "description": "University/institution name", "default": "N/A"},
                    "location": {"type": "string", "description": "Institution location", "default": "N/A"},
                    "year": {"type": "string", "description": "Years attended", "default": "N/A"},
                    "grade": {"type": "string", "description": "Final grade or distinction", "default": "N/A"}
                }
            },
            "default": []
        },
        "experience": {
            "type": "array",
            "description": "List of work experiences",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Job title", "default": "N/A"},
                    "company": {"type": "string", "description": "Company name", "default": "N/A"},
                    "location": {"type": "string", "description": "Company location", "default": "N/A"},
                    "year": {"type": "string", "description": "Employment year(s)", "default": "N/A"},
                    "domain": {"type": "string", "description": "Field of work", "default": "N/A"},
                    "responsibilities": {
                        "type": "array",
                        "description": "Key responsibilities in bullet points",
                        "items": {"type": "string"},
                        "default": []
                    }
                }
            },
            "default": []
        },
        "skills": {
            "type": "array",
            "description": "List of technical and soft skills",
            "items": {"type": "string"},
            "default": []
        },
        "certifications": {
            "type": "array",
            "description": "List of certifications obtained",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Certification name", "default": "N/A"},
                    "year": {"type": "string", "description": "Year obtained", "default": "N/A"}
                }
            },
            "default": []
        }
    },
    "required": ["name", "contact", "education", "experience"]
}

autofill_json_schema = {
    "title": "form_fields_filled",
    "description": "Autofilling job application fields",
    "type": "object",
    "properties": {
        "fields": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fieldType": {"type": "string"},
                    "label": {"type": "string"},
                    "action": {"type": "string"},
                    "selector": {"type": "string"},
                    "sectionLabel": {"type": "string"},
                    "sectionSelector": {"type": "string"},
                    "value": {"type": "string"},
                    "times": {"type": "integer"}
                },
                "required": [
                    "fieldType", "label", "action", "selector",
                    "sectionLabel", "sectionSelector"
                ],
                "additionalProperties": False
            }
        }
    },
    "required": ["fields"]
}

