from .common_prompt_parts import (
    response_format,
    base_formatting,
    closing_rules
)
def get_aws_prompt(log_text):

    return f"""
    You are a senior AWS cloud engineer.

     Analyze this AWS infrastructure issue:

    {log_text}

    {base_formatting}

    Focus on:
    Focus on:
    - IAM permissions
    - EC2
    - Security Groups
    - NACLs
    - Route Tables
    - VPC / Subnet configuration
    - CloudWatch logs
    - AWS CLI troubleshooting
    - Terraform-created AWS resources when relevant

    {response_format}

    {closing_rules}
    """