@echo off
echo Starting MWF 9am EST Cadence
echo.
echo Running Curation Join...
C:\Users\J\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe "C:\Users\J\Documents\LLM\cardscout-2.0\src\mass_pipeline\customer_curation.py"
echo.
echo Running Digest Delivery...
C:\Users\J\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe "C:\Users\J\Documents\LLM\card-scout\scripts\digest_delivery.py" %*
echo.
echo MWF Cadence Complete.
