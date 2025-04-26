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


autofill_schema = {
    "title": "ai_autofill",
    "description": "AI-generated mapping of extracted form fields to user profile data.",
    "type": "object",
    "properties": {
        "form_fields_filled": {
            "type": "array",
            "description": "List of form fields and their AI-matched actions and values.",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name attribute of the form field.",
                        "default": "N/A"
                    },
                    "id": {
                        "type": "string",
                        "description": "The id attribute of the form field (if available).",
                        "default": "N/A"
                    },
                    "label": {
                        "type": "string",
                        "description": "The visible label of the field.",
                        "default": "N/A"
                    },
                    "type": {
                        "type": "string",
                        "description": "Type of HTML element (input, select, checkbox, radio, textarea, button).",
                        "enum": ["input", "select", "checkbox", "radio", "textarea", "button"],
                        "default": "input"
                    },
                    "fieldType": {
                        "type": "string",
                        "description": "Specific type of input (e.g., text, email, submit, file, etc.).",
                        "default": "text"
                    },
                    "classList": {
                        "type": "string",
                        "description": "CSS class names associated with the field (space-separated).",
                        "default": "N/A"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform on the field: 'click', 'type', 'select', or 'check'.",
                        "enum": ["click", "type", "select", "check"],
                        "default": "type"
                    },
                    "times": {
                        "type": "integer",
                        "description": "Number of times to repeat the action (only for 'click' actions).",
                        "minimum": 1
                    },
                    "value": {
                        "type": "string",
                        "description": "The value to type or select for the field (only for 'type' and 'select' actions).",
                        "default": "N/A"
                    }
                },
                "required": ["name", "id", "type", "action"]
            }
        }
    },
    "required": ["form_fields_filled"]
}
