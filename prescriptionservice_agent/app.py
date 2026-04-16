"""
prescriptionservice_agent — A2A application entry point.

Start the server with:
    python3 -m uvicorn prescriptionservice_agent.app:a2a_app --host 0.0.0.0 --port 8009

To ensure all modules are found, run this command from the project root directory.

The agent card is served publicly at:
    GET http://localhost:8009/.well-known/agent-card.json

All other endpoints require an X-API-Key header (see shared/middleware.py).
"""
import os

from a2a.types import AgentSkill, AgentInterface
from shared.app_factory import create_a2a_app

from .agent import root_agent

print(os.getenv('PO_PLATFORM_BASE_URL'))

a2a_app = create_a2a_app(
    agent=root_agent,
    name="prescriptionservice_agent",
    description=(
        "A clinical assistant that queries a patient's prescription record to answer "
        "questions about medications, conditions, and observations."
    ),
    url=os.getenv("PRESCRIPTIONSERVICE_AGENT_URL", os.getenv("BASE_URL", "http://localhost:8009")),
    port=8009,
    # This URI is the key under which callers send FHIR credentials in the
    # A2A message metadata.  Update to match your Prompt Opinion workspace URL.
        # This URI is the key under which callers send FHIR credentials in the
    # A2A message metadata.  Update to match your Prompt Opinion workspace URL.
    fhir_extension_uri=f"{os.getenv('PO_PLATFORM_BASE_URL', 'http://localhost:5139')}/schemas/a2a/v1/fhir-context",
    # SMART-on-FHIR scopes — one per FHIR resource type accessed by the tools.
    # All are marked required because each tool will fail without its scope.
    fhir_scopes=[
        {"name": "patient/Patient.rs",           "required": True},   # get_patient_demographics
        {"name": "patient/MedicationRequest.rs", "required": True},   # get_active_medications
        {"name": "patient/Condition.rs",         "required": True},   # get_active_conditions
        {"name": "patient/Observation.rs",       "required": True},   # get_recent_observations
    ],
    skills=[
        AgentSkill(
            id="generate_prescription",
            name="generate_prescription",
            description="Generate a prescription for a patient based on their risk factors.",
            tags=["prescriptions", "fhir"],
        ),
        AgentSkill(
            id="calculate_risk_factors",
            name="calculate_risk_factors",
            description="Calculate risk factors for a patient based on their FHIR record.",
            tags=["risk-factors", "fhir"],
        ),
    ],
)
