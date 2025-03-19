from langchain_core.tools import tool

from typing import Any, Dict

import jsonschema
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


@tool
def validate_json_data(json_schema: Dict[str, Any], json_data: Dict[str, Any]) -> str:
    """
    Validates if JSON data conforms to JSON Schema.

    Args:
        schema: The JSON schema to validate.
        data: The JSON data to validate against the schema.

    Returns:
        str: "Validation successful" if valid.

    Raises:
        ValidationError: If the JSON schema is invalid or the data does not conform to the schema.
    """
    try:
        # Validate the schema itself
        Draft202012Validator.check_schema(json_schema)

        # Validate the data against the schema
        jsonschema.validate(instance=json_data, schema=json_schema)

        return "Validation successful"

    except ValidationError as e:
        return f"Validation failed: {e.message}"


@tool
def validate_json_schema(json_schema: Dict[str, Any]) -> str:
    """
    Validates a JSON schema.

    Args:
        schema: The JSON schema to validate.

    Returns:
        str: "Validation successful" if valid.

    Raises:
        ValidationError: If the JSON schema is invalid.
    """
    try:
        Draft202012Validator.check_schema(json_schema)
    except ValidationError as e:
        return f"Invalid JSON Schema: {e.message}"

    return "Validation successful"
