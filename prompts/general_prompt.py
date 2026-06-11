from .common_prompt_parts import (
    response_format,
    base_formatting,
    closing_rules
)
def get_general_prompt(log_text):

    return f"""

     You are a senior infrastructure support engineer.

     Analyze this issue:

    {log_text}
    {base_formatting}

     Focus on:
    - Networking
    - DNS
    - Authentication
    - Linux and Windows server behavior
    - Cloud infrastructure
    - Log analysis
    - Infrastructure dependencies
    - Common configuration issues

    {response_format}

    {closing_rules}
    """