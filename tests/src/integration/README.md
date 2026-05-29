<!--
Copyright 2026 IBM Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
# Integration Tests

This directory contains integration tests for the data-intelligence-sdk modules that require external service connections.

## Overview

Integration tests verify that the SDK works correctly with actual IBM Cloud services. These tests are skipped by default when the required configuration files are not present.

## Test Files

### 1. `test_dph_v1.py`
Tests for IBM Data Product Hub API Service (DPH Services).

**Requirements:**
- Configuration file: `dph_v1.env`
- Valid IBM Cloud API credentials
- Access to IBM Data Product Hub service

**Tests:** 49 integration tests covering:
- Container initialization
- Data product CRUD operations
- Draft management
- Release management
- Contract terms and documents
- Domain management

### 2. `test_odcs_generator_collibra.py`
Tests for ODCS generation from Collibra.

**Requirements:**
- Collibra API credentials
- Sample Collibra data assets

### 3. `test_odcs_generator_informatica.py`
Tests for ODCS generation from Informatica.

**Requirements:**
- Informatica API credentials
- Sample Informatica data assets

### 4. `test_data_product_recommender_integration.py`
Tests for data product recommendation engine.

**Requirements:**
- Sample query log data files
- Database connection (if testing with live data)

## Configuration Setup

### DPH Services Configuration (`dph_v1.env`)

The `test_dph_v1.py` integration tests require a configuration file named `dph_v1.env` in this directory.

#### Step 1: Copy the Template

A template file `dph_v1.env` has been created in this directory. Edit it with your credentials.

#### Step 2: Get IBM Cloud API Key

1. Log in to [IBM Cloud](https://cloud.ibm.com/)
2. Navigate to **Manage** > **Access (IAM)** > **API keys**
3. Click **Create** to create a new API key
4. Copy the API key (you won't be able to see it again)

#### Step 3: Configure the File

Edit `tests/integration/dph_v1.env` and replace the placeholder values:

```bash
# Required: Service URL
DATA_PRODUCT_HUB_API_SERVICE_URL=https://api.dataplatform.cloud.ibm.com/

# Required: Authentication type
DATA_PRODUCT_HUB_API_SERVICE_AUTH_TYPE=iam

# Required: Your IBM Cloud API Key
DATA_PRODUCT_HUB_API_SERVICE_APIKEY=your-actual-key-here
```

#### Step 4: Verify Permissions

Ensure your API key has the following permissions:
- Access to IBM Data Product Hub service
- Ability to create/read/update/delete data products
- Access to the target catalog/container

### Configuration File Format

The IBM Cloud SDK uses environment variables or configuration files in the following format:

```
<SERVICE_NAME>_URL=<service-url>
<SERVICE_NAME>_AUTH_TYPE=<auth-type>
<SERVICE_NAME>_APIKEY=<key>
```

Where `<SERVICE_NAME>` is the uppercase version of the service name with underscores.

For DPH Services, the service name is `data_product_hub_api_service`, so variables are prefixed with `DATA_PRODUCT_HUB_API_SERVICE_`.

## Running Integration Tests

### Run All Integration Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all integration tests
pytest tests/integration/ -v
```

### Run Specific Test File

```bash
# Run only DPH integration tests
pytest tests/integration/test_dph_v1.py -v

# Run only ODCS Collibra tests
pytest tests/integration/test_odcs_generator_collibra.py -v
```

### Run with Coverage

```bash
pytest tests/integration/ --cov=src/wxdi --cov-report=html
```

## Test Behavior

### Without Configuration
When configuration files are missing, tests are automatically skipped with the message:
```
SKIPPED [49] External configuration not available, skipping...
```

### With Configuration
When valid configuration is provided, tests will:
1. Connect to the actual IBM Cloud service
2. Perform real API operations
3. Validate responses and behavior
4. Clean up resources (where applicable)

## Security Notes

⚠️ **IMPORTANT SECURITY CONSIDERATIONS:**

1. **Never commit credentials**: The `.env` files contain sensitive API keys and should NEVER be committed to version control
2. **Already protected**: The `.gitignore` file already excludes `.env` files
3. **Secure sharing**: Share credentials only through secure channels (password managers, encrypted communication)
4. **Rotate keys**: Regularly rotate API keys, especially if they may have been exposed
5. **Minimal permissions**: Use API keys with the minimum required permissions

## Troubleshooting

### Tests are Skipped

**Problem:** All integration tests show as "skipped"

**Solution:**
- Verify the configuration file exists: `tests/integration/dph_v1.env`
- Check that the file contains valid credentials
- Ensure the file is in the correct location

### Authentication Errors

**Problem:** Tests fail with 401 Unauthorized or 403 Forbidden

**Solution:**
- Verify your API key is correct and not expired
- Check that your API key has the required permissions
- Ensure the service URL is correct for your region

### Connection Errors

**Problem:** Tests fail with connection timeouts or network errors

**Solution:**
- Verify the service URL is correct
- Check your network connection
- Ensure you can access IBM Cloud services from your network
- Check if there are any firewall restrictions

### Service-Specific Errors

**Problem:** Tests fail with service-specific error messages

**Solution:**
- Check the IBM Data Product Hub service status
- Verify your account has access to the service
- Review the test output for specific error messages
- Consult IBM Cloud documentation for the specific service

## Additional Resources

- [IBM Cloud SDK Core Documentation](https://github.com/IBM/python-sdk-core)
- [IBM Cloud Authentication Guide](https://cloud.ibm.com/docs/account?topic=account-userapikey)
- [IBM Data Product Hub Documentation](https://cloud.ibm.com/docs/data-product-hub)
- [pytest Documentation](https://docs.pytest.org/)

## Support

For issues related to:
- **SDK functionality**: Open an issue in the data-intelligence-sdk repository
- **IBM Cloud services**: Contact IBM Cloud Support
- **Authentication**: Refer to IBM Cloud IAM documentation