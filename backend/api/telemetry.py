import os
from dotenv import load_dotenv

load_dotenv()


def setup_phoenix():
    """Register Arize Phoenix OTEL tracer and instrument ADK."""
    api_key = os.getenv("PHOENIX_API_KEY")
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "https://app.phoenix.arize.com")
    project = os.getenv("PHOENIX_PROJECT_NAME", "matchmind-hackathon")

    if not api_key:
        print("PHOENIX_API_KEY not set — skipping telemetry setup")
        return

    try:
        from phoenix.otel import register
        from openinference.instrumentation.google_adk import GoogleADKInstrumentor

        register(
            project_name=project,
            endpoint=f"{endpoint}/v1/traces",
            headers={"api_key": api_key},
        )
        GoogleADKInstrumentor().instrument()
        print(f"Phoenix telemetry active → project: {project}")
    except Exception as e:
        # never crash the server over observability
        print(f"Phoenix setup failed (non-fatal): {e}")
