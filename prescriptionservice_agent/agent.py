"""
prescriptionservice_agent — Agent definition.

This agent has read-only access to a patient's FHIR R4 record.
FHIR credentials (server URL, bearer token, patient ID) are injected via the
A2A message metadata by the caller (e.g. Prompt Opinion) and extracted into
session state by extract_fhir_context before every LLM call.

To customise:
  • Change model, description, and instruction below.
  • Add or remove tools from the tools=[...] list.
  • Add new FHIR tools in shared/tools/fhir.py and export from shared/tools/__init__.py.
  • Add non-FHIR tools in shared/tools/ or locally in a tools/ folder here.
"""
from google.adk.agents import Agent

from shared.fhir_hook import extract_fhir_context

from shared.tools.fhir import (
    generate_prescription_tool,
    calculate_risk_factors_tool,
)


root_agent = Agent(
    name="prescriptionservice_agent",
    model="gemini-2.5-flash",
    description=(
        "PrescriptionServiceAgent generates a structured and clinically accurate prescription summary "
        "based on provided patient diagnosis and medication data. It ensures clarity, correctness, and "
        "professional formatting without introducing new medical assumptions. Also provide risks associated with the diagnosis."
    ),
    instruction=(
        "You are PrescriptionServiceAgent, a helpful clinical assistant. "
        "Use the available tools to answer questions accurately. "
        "Your task is to generate a clear, structured, and professional prescription summary."
        "Clearly present the diagnosis: "
        "- List each condition with a brief description"
        "- Include any relevant modifiers (e.g., stage, severity)"
        "List each medication with dosage and instructions: "
        "- Include the name, dosage, and instructions for each medication"
        "- If a medication is prescribed more than once, list all instances"
        "Include lifestyle recommendations: "
        "- List any recommended lifestyle changes (e.g., diet, exercise)"
        "- Keep the output concise, readable, and clinically appropriate"
        "Do NOT introduce new medications or assumptions: "
        "- Never add or modify medications or recommendations without explicit patient approval"
        "- Avoid suggesting new diagnoses or treatments"
        "Provide a structured summary of risks based on the diagnosis: "
        "- List any potential side effects or risks associated with the prescribed medications"
        "- Mention any precautions or warnings related to the patient's condition"
        "Output Format: "
        "- Diagnosis: List each condition with a brief description"
        "- Medications: Include the name, dosage, and instructions for each medication"
        "- Lifestyle Advice: List any recommended lifestyle changes (e.g., diet, exercise)"
    ),
    tools=[
        generate_prescription_tool,
        calculate_risk_factors_tool,
    ],
    # Runs before every LLM call.
    # Reads fhir_url, fhir_token, and patient_id from A2A message metadata
    # and writes them into session state so tools can call the FHIR server.
    before_model_callback=extract_fhir_context,
)
