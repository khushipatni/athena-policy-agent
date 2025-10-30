# PDF Underwriter AI Agent

## Overview
This AI agent reads a **loan policy PDF**, extracts the lending criteria, and evaluates **loan applications** based on those rules.  
It uses **Gemini (Google Generative AI)** to reason over the policy and application, returning a clear decision and explanation.

---

## Features
- Parses loan underwriting policies directly from PDFs.
- Evaluates loan applications with credit score, DTI, income, and employment checks.
- Produces structured JSON output:
  ```json
  {
    "decision": "approved" | "denied",
    "reasoning": "Detailed explanation of the decision",
    "riskLevel": "low" | "medium" | "high"
  }
  ```
- Uses Gemini’s API for AI reasoning with a deterministic fallback.

---

## Project Structure
```
pdf-underwriter/
├── README.md
├── requirements.txt
├── src/
│   │
│   ├── main.py                         # Entry point — loads policy + app, calls AI agent
│   │
│   ├── agents/                         # All AI logic
│   │   └── policy_agent.py             # Main underwriting AI (Gemini + deterministic logic)
│   │
│   └──  utils/                         # Helper utilities
│       └── policy_parser.py            # Extracts rules/criteria from the policy PDF
└── examples/
    ├── loan_policy.pdf                 # Sample input policy
    ├── app.json                        # Example applicant (approved)
    ├── app2.json                       # Example applicant (denied)
    └── app3.json                       # Example applicant (denied)

```

---

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/khushipatni/athena-policy-agent.git
   cd athena-policy-agent
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set your Gemini API key**
   - Get a free API key from [Google AI Studio](https://aistudio.google.com/api-keys)
   - Then export it:
     ```bash
     export GEMINI_API_KEY="your_api_key_here"
     ```

---

## Run the Agent

Make sure your sample files (`loan_policy.pdf` and `app.json`) are in the same folder as `main.py`.

Then run:
```bash
python3 src/main.py --policy examples/loan_policy.pdf --app examples/app.json
```

### Example Output
```json
{
  "decision": "approved",
  "reasoning": "Credit score 690 falls in medium-risk category (650-719).\nDebt-to-income ratio: 29.6% (within 30% limit for medium-risk)\nEmployment: 18 months (meets 12-month minimum)",
  "riskLevel": "medium"
}
```

---

## Example Application (`app.json`)
```json
{
  "applicantId": "APP_001",
  "requestedAmount": 250000,
  "annualIncome": 85000,
  "monthlyDebt": 2100,
  "creditScore": 690,
  "employmentMonths": 18,
  "isFirstTimeBuyer": false,
  "isSelfEmployed": false
}
```

---

## Tools Used
- **Python 3.12.7+**
- **pdfplumber** – PDF text extraction  
- **pydantic** – Schema validation  
- **google-generativeai** – Gemini model integration  

---

## Process & Architecture

### Overview
The project follows a simple, modular flow designed for clarity and scalability:
> **PDF Policy → Extracted Rules → AI Agent → Decision JSON**

### 1. **`policy_parser.py` – Policy Understanding**
- Reads the PDF and extracts key underwriting rules.  
- Identifies **credit score tiers**, **DTI thresholds**, **income requirements**, and **special cases**.  
- Outputs structured text ready for the AI agent to reason on.  

### 2. **`agent.py` – Decision Engine**
- Combines the **policy text** and **applicant data**, then sends it to **Gemini**.  
- The AI interprets the rules, applies them, and returns a structured JSON decision.  
- If Gemini’s response is invalid or incomplete, a deterministic (rule-based) fallback ensures reliability.  

### 3. **`main.py` – Orchestration Layer**
- Acts as the project’s **entry point**.  
- Loads the inputs (policy + application), runs the parser, invokes the agent, and prints a clean JSON result to the console.  

---

## Future Improvements
This section outlines enhancements planned for both the **AI Agent** and the **Application Infrastructure**.

---

### Agent Improvements

1. **Few-shot prompting & JSON mode:**  
   Use structured prompting with sample decisions to improve Gemini’s reliability and ensure perfectly formatted JSON outputs.

2. **Hybrid rule extraction:**  
   Combine deterministic regex parsing with AI-based summarization to handle complex or irregular policy documents efficiently.

3. **Policy caching & versioning:**  
   Cache parsed policies using PDF hashes — skip redundant parsing for repeated evaluations.

4. **Explainability & provenance:**  
   Include which policy section or rule influenced the decision, with clear, audit-friendly reasoning.

5. **Dynamic model routing:**  
   Select models dynamically — e.g., use cheaper LLMs for simple policies and advanced models for complex ones.

6. **Evaluation suite:**  
    Automate validation across test applicants; measure accuracy, latency, and cost per inference.

---

### Application Improvements

1. **Containerization (Docker):**  
   Package the entire app with dependencies into a Docker image for reproducible runs and easy deployment.

2. **API service (FastAPI):**  
   Expose underwriting as a REST API endpoint:
   - `/underwrite` – runs single applicant decision  
   - `/batch` – handles multiple applicants  

3. **Logging & observability:**  
   Add structured logging (JSON logs) for every request with timestamps, applicant IDs, DTI calculations, and LLM token usage.

4. **Testing & regression suite:**  
   Automate tests for PDF parsing, deterministic rule application, and LLM decision accuracy.

5. **Cloud readiness:**  
   Prepare the container to run as a service on Google Cloud Run, AWS Lambda, or Azure Functions.

6. **Configuration management:**  
   Use `.env` or YAML configs for environment variables like API keys, model names, and thresholds.

7. **Security & governance:**  
   Handle sensitive financial data securely, enable HTTPS and token-based authentication for API endpoints.

8. **Performance optimization:**  
    Cache policy summaries, reuse embeddings, and manage parallel underwriting to reduce latency and cost.

---

## Summary
✅ **Input 1:** PDF underwriting policy  
✅ **Input 2:** Loan application JSON  
✅ **Output:** Approval decision + reasoning + risk level  
✅ **Tech:** Python + Gemini API  