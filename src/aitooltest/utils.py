from pydantic import BaseModel
from typing import get_args, get_origin, Union, List, Optional, Dict, Any


def generate_schema(model: type[BaseModel]) -> Dict[str, Any]:
    """Convert a Pydantic model into a Google Gemini-style parameter schema."""
    properties = {}
    required_fields = []

    for field_name, field in model.model_fields.items():
        field_info = field
        field_type = field.annotation

        # Determine JSON schema type
        json_type = python_type_to_json_type(field_type)
        field_schema = {"type": json_type}

        # Add description if available
        if field_info.description:
            field_schema["description"] = field_info.description

        properties[field_name] = field_schema

        # Required fields (no default and not Optional)
        if field_info.is_required():
            required_fields.append(field_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required_fields,
    }


def python_type_to_json_type(py_type: Any) -> str:
    """Map Python/Pydantic types to JSON Schema types."""
    origin = get_origin(py_type)
    if origin is Union:
        args = get_args(py_type)
        # Handle Optional[X]
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return python_type_to_json_type(non_none[0])
        else:
            return "object"  # fallback

    mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    return mapping.get(py_type, "object")
