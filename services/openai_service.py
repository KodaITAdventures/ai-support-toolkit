from openai import OpenAI
from openai import AuthenticationError
from openai import APITimeoutError

from dotenv import load_dotenv
import os
import markdown

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_ai_response(prompt):

    try:

        ai_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return markdown.markdown(
            ai_response.choices[0].message.content,
            extensions=["fenced_code"]
        )

    except AuthenticationError:

        return """
        <div class='error-box'>
            Invalid OpenAI API key.
            <br><br>
            Check your .env configuration and restart the application.
        </div>
        """

    except APITimeoutError:

        return """
        <div class='error-box'>
            OpenAI request timed out.
            <br><br>
            Please try again.
        </div>
        """

    except Exception as e:

        return f"""
        <div class='error-box'>
            Error communicating with OpenAI API.
            <br><br>
            Details:
            <br>
            {str(e)}
        </div>
        """