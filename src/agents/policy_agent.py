import os, json, google.generativeai as genai
from pydantic import BaseModel
from typing import Literal
import re

class AppData(BaseModel):
    applicantId: str
    requestedAmount: int
    annualIncome: float
    monthlyDebt: float
    creditScore: int
    employmentMonths: int
    isFirstTimeBuyer: bool
    isSelfEmployed: bool

class Output(BaseModel):
    decision: Literal["approved","denied"]
    reasoning: str
    riskLevel: Literal["low","medium","high"]

def call_gemini(policy_text: str, app: AppData) -> Output:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash-lite")

    prompt = f"""
                You are an underwriting AI system responsible for two tasks:
                1. Validate the provided loan policy document for completeness and logical consistency.
                2. Apply it accurately to the applicant data to reach a decision.

                You must return output that exactly matches this JSON schema:

                {{
                "decision": "approved" | "denied",
                "reasoning": "string (detailed explanation; include validation or underwriting reasoning)",
                "riskLevel": "low" | "medium" | "high"
                }}

                ### VALIDATION RULES
                Before making a decision, check if the policy text is internally consistent and usable:
                - Ensure **credit score tiers** are numeric and non-overlapping (e.g., 650–719, 720+).
                - Ensure **DTI limits** exist for each tier and are positive percentages.
                - Ensure **income requirements** and **employment months** are clearly defined and positive.
                - If any of the above are missing, contradictory, or non-numeric, mark the decision as `"denied"` and include
                  a proper reason in the reasoning.
                - If the policy appears malformed or inconsistent, do **not** attempt underwriting — only report the validation issue.

                ### UNDERWRITING Rules
                - Use ONLY lowercase values for "decision" and "riskLevel".
                - "riskLevel" must be exactly one of: "low", "medium", or "high" — never "low risk" etc.
                - Follow the provided policy and calculate DTI.
                - If applicant violates any rule, explain why in reasoning.
                - Never include markdown, code fences, or additional text outside the JSON.
                - Do not restate the prompt, just return the JSON.

                Policy text:
                {policy_text}

                Loan Application JSON:
                {app.model_dump_json(indent=2)}

                Now perform:
                1. Validate the policy structure and logic.
                2. If valid, apply underwriting rules.
                3. Output ONLY the final JSON object as per the schema above.
            """

    resp = model.generate_content(prompt)

    # --- extract JSON text safely ---
    text = ""
    if hasattr(resp, "text") and resp.text:
        text = resp.text.strip()
    else:
        # handle Gemini candidates API object
        try:
            text = "".join(p.text for c in resp.candidates for p in c.content.parts)
        except Exception:
            text = str(resp)

    # Remove markdown fences if present
    text = re.sub(r"^```(json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())

    try:
        data = json.loads(text)
        # Normalize keys to lowercase for robustness
        data = {k.lower(): v for k, v in data.items()}
        # ensure required fields
        return Output(
            decision=data.get("decision", "").lower(),
            reasoning=data.get("reasoning", ""),
            riskLevel=data.get("risklevel", "").lower()
        )
    except Exception as e:
        print("JSON parsing error:", e)
        print("Response text was:\n", text)
        return Output(
            decision="denied",
            reasoning="Could not parse model output",
            riskLevel="high"
        )
