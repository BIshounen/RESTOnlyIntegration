# REST-Only Integration Example for Nx VMS

This integration example demonstrates how to create a simple integration for Nx VMS that registers itself and, upon approval, can use VMS endpoints to generate simple events and objects.

## Overview

The integration follows this logic:

1. Check if the integration has already tried to register by looking for a credentials file.
2. If no credentials file exists:
   - Send a registration request
   - Store integration user credentials in the file
   - Finish execution
3. If credentials file exists:
   - Check if the integration has been approved by getting user parameters from the VMS
4. If approved:
   - Get the Integration ID from user's additional parameters
   - Get the Engine ID
   - Get the first Device Agent ID for the Engine
5. If a Device Agent is found:
   - Send one Event and one Object using data from a JSON file
   - Add timestamp, duration, and engine ID to the request data

## Prerequisites

- Nx VMS server
- Access to VMS REST API endpoints
- Python environment

## Notes

- The credentials file is not included in the git repository for security reasons.
- Make sure to enable the integration on at least one device in Nx VMS for successful execution.
- If the integration is not approved or not enabled on any device, the script will finish with an appropriate message or error.
