response_format = """
Respond with:

## Likely Issue
- Bullet points only
- Prioritize the most likely root cause first
- Avoid listing too many unlikely possibilities

## Severity
- One short sentence
- Use Low, Medium, High, or Critical when appropriate

## Troubleshooting Steps
1. Use clean numbered steps
2. Keep steps practical and actionable
3. Focus on production troubleshooting workflows

## Recommended Commands
- Include only relevant commands/checks when applicable
- Use markdown code blocks for commands

## Additional Notes
- Bullet points only
- Mention what information is missing if needed
- Mention assumptions if making educated guesses
"""

base_formatting = """
FORMATTING RULES:
- Use proper markdown
- Use clean numbered lists only where steps are sequential
- Use bullets for likely causes and notes
- Keep bullet points to 1-2 sentences maximum
- Do not leave blank numbered items
- Keep sections concise
- Use fenced code blocks for commands
- Do not repeat section headers
- Avoid excessive spacing
- If information is missing, say what to check next instead of guessing
- Do not invent logs, commands, configurations, or results that were not provided
- Clearly state when more information is required
- Avoid excessive blank lines between sections or list items
"""

closing_rules = """
Keep responses concise, technical, and production-oriented.
Avoid generic helpdesk advice.
Do not explain basic concepts unless directly relevant.
Focus on actionable troubleshooting steps.
"""
