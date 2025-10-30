import json
import argparse
from utils import policy_parser
from agents import policy_agent
from pydantic import ValidationError

def main():
    # ---------- ARGUMENT PARSING ----------
    parser = argparse.ArgumentParser(
        description="Run the Athena Loan Underwriting AI Agent"
    )
    parser.add_argument(
        "--policy",
        required=True,
        help="Path to the loan policy PDF file (e.g., loan_policy.pdf)"
    )
    parser.add_argument(
        "--app",
        required=True,
        help="Path to the loan application JSON file (e.g., app.json)"
    )

    args = parser.parse_args()

    # ---------- LOAD INPUTS ----------
    policy_text = policy_parser.extract_text(args.policy)
    with open(args.app, "r") as f:
        app_data = json.load(f)

    try:
        app = policy_agent.AppData(**app_data)
    except ValidationError as ve:
        print("\nValidation Error in Loan Application JSON:\n")
        for err in ve.errors():
            field = err.get("loc", ["?"])[0]
            msg = err.get("msg", "")
            print(f"  - Field '{field}': {msg}")
        print("\nPlease ensure all required fields are present and valid.\n")
        return  # stop execution gracefully

    # ---------- DISPLAY APPLICATION ----------
    print("\n📄 Loan Application Input:")
    print(json.dumps(app.model_dump(), indent=2))

    # ---------- RUN AGENT ----------
    print("\n🤖 Running AI Underwriting Agent...\n")
    result = policy_agent.call_gemini(policy_text, app)

    # ---------- DISPLAY RESULT ----------
    print("✅ Underwriting Decision:")
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()
