document_requirements: list[str] = []

MODEL_INPUT_SCHEMA = {
    "document_metadata": {
        "name": "ExtractDocumentInfo",
        "schema": {
            "type": "object",
            "properties": {
                "document_name": {"type": "string"},
                "document_author": {"type": "string"},
                "document_publication_date": {"type": "string", "format": "date"},
                "document_type": {"type": "string"},
                "document_toc": {"type": "array", "items": {"type": "string"}},
                "document_summary": {"type": "string"},
            },
            "required": [
                "document_name",
                "document_author",
                "document_publication_date",
                "document_type",
                "document_toc",
                "document_summary",
            ],
        },
    },
    "image_analysis_regular": {
        "name": "ImageAnalysisInfo",
        "schema": {
            "type": "object",
            "properties": {
                "image_name": {"type": "string", "description": "Name of the image"},
                "image_description": {
                    "type": "string",
                    "description": "Description of the image",
                },
            },
            "required": ["image_name", "image_description"],
        },
    },
    "validation": {
            "name": "document_review",
            "description": "Validation and comments for each document checklist item.",
            "schema": {
                "type": "object",
                "properties": {
                    "reviews": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "document_type": {
                                    "type": "string",
                                    "enum": document_requirements,
                                    "description": "Type of document, must match the reference list exactly.",
                                },
                                "validation_result": {
                                    "type": "string",
                                    "enum": [
                                        "Fully satisfied",
                                        "Partially satisfied",
                                        "Not satisfied",
                                    ],
                                    "description": "Result of validation.",
                                },
                                "comments": {
                                    "type": "string",
                                    "description": "Reviewer comments.",
                                },
                            },
                            "required": [
                                "document_type",
                                "validation_result",
                                "comments",
                            ],
                        },
                        "minItems": 1,
                    }
                },
                "required": ["reviews"],
            }
    }
}
