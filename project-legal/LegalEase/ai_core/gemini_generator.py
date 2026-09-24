import os
import time
from textwrap import dedent

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


SYSTEM_INSTRUCTION = """
You are LegalEase, an AI assistant that drafts structured legal-document
templates from user-provided facts.

Important:
- Produce a professional TEMPLATE, not a claim that the document is legally
  valid in every jurisdiction.
- Do not invent names, dates, addresses, prices, obligations, laws, statutes,
  or facts that the user did not provide.
- Preserve the user's supplied facts accurately.
- Use neutral, formal legal language.
- Include clearly labeled sections.
- If a critical fact is missing, use [TO BE COMPLETED] rather than inventing it.
- End with a short "Review Notice" telling the user to have the document
  reviewed by a qualified lawyer before signing or relying on it.
- Return only the document text. Do not wrap it in Markdown code fences.
"""


class GeminiDocumentGenerator:
    """Generate LegalEase documents through Google's current GenAI Python SDK."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. Add it to the .env file."
            )

        self.client = genai.Client(api_key=self.api_key)

    def build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:
        return dedent(
            f"""
            Draft a complete {document_type} template using exactly the
            information supplied below.

            Document type:
            {document_type}

            Parties:
            {parties}

            Effective date:
            {effective_date}

            Terms and conditions:
            {terms}

            Required structure:
            1. Document title
            2. Introduction / parties
            3. Purpose
            4. Definitions where useful
            5. Main obligations and rights
            6. Payment / consideration if applicable
            7. Confidentiality / intellectual property if applicable
            8. Term and termination if applicable
            9. Dispute / governing-law section as a placeholder if the
               jurisdiction was not supplied
            10. General provisions
            11. Signature blocks
            12. Review Notice

            Formatting rules:
            - Use uppercase section headings.
            - Use numbered clauses.
            - Keep the output editable as plain text.
            - Do not fabricate jurisdiction-specific legal requirements.
            """
        ).strip()

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:
        prompt = self.build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
        )

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.25,
                        max_output_tokens=5000,
                    ),
                )
                break
            except Exception as exc:
                status_code = str(getattr(exc, "code", ""))
                if status_code not in {"429", "500", "503"}:
                    raise
                if attempt == 2:
                    raise RuntimeError(
                        "Gemini is temporarily unavailable. Please try again shortly."
                    ) from exc
                time.sleep(2**attempt)

        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")

        return text.strip()
