# Use Case 15: Automating document validation checks

## Overview

In this use case, we show how to integrate large language models (LLMs) into supervisory document validation workflows to automate and enhance the process of checking document submissions against defined submission requirements such as in relation to the type and scope of documents. To mimic a realistic working environment more closely, we demonstrate how to access and organize source documents through a SharePoint connection and library as well as set up our pipeline to cater for a document types, ranging from text-based files to scanned images and PDFs.

Our pipeline consists of five principal steps:

* Step 1: Establishing a connection to the SharePoint site where the documents subject to validation are stored using the Microsoft Graph API
* Step 2: Automatically extract textual content from all files in the specified source folder, using a variety of extraction techniques including OCR to accommodate for diverse document types
* Step 3: Applying LLMs to generate structured metadata for each document including details on the document type, its title, content and principal sections
* Step 4: Leveraging LLMs to compare the submitted documents on the basis of the extracted metadata against pre-defined document submission requirements using a structured validation approach 
* Step 5: Consolidating validation results in a structured Word report for further review by supervisors

For this use case, no sample input files or requirements are provided. Users are expected to define their own document requirements for validation and supply their own SharePoint files for testing purposes.

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>


## Structure of the use case directory

```

use_case_15/
│
├── input/
│   - Placeholder for user-supplied input files such as document_requirements.json
│
├── output/
│   - Results of document extraction and validation (e.g., document_list.json, validation results)
│
├── prompts/
│   ├── PROMPT_IMAGE_EXTRACTION_OCR.txt       # Prompt for OCR-based image extraction
│   ├── PROMPT_IMAGE_EXTRACTION_REGULAR.txt   # Prompt for regular image description
│   ├── PROMPT_METADATA_EXTRACTION.txt        # Prompt for extracting structured metadata
│   └── PROMPT_VALIDATION.txt                 # Prompt for LLM document validation
│
├── content_management/
│   ├── content_extraction_manager.py         # Handles downloading and extracting text/images from SharePoint files
│   └── metadata_manager.py                   # Extracts file metadata and document-level metadata
│
├── processors/
│   ├── directory_manager.py                  # Handles traversal, extraction, and migration of SharePoint folders/files
│   ├── extraction_pipeline.py                # Orchestrates document extraction from SharePoint
│   ├── validation_processor.py               # Executes the validation logic against requirements
│   ├── validation_pipeline.py                # Orchestrates the validation process and report generation
│   └── parser.py                             # Utilities for parsing files and type detection
│
├── services/
│   ├── graph_client.py                       # Handles authentication and API calls to Microsoft Graph (SharePoint)
│   └── llm_client.py                         # Handles LLM communication (OpenAI/Azure OpenAI)
│
├── utils/
│   ├── helpers.py                            # Helper utilities for logging and JSON handling
│   ├── schemas.py                            # Input/output schemas for LLMs and validation
│   └── utils.py                              # Utility functions for content extraction and conversion
│
├── model_config.yml                          # LLM model and provider configuration
├── processor.py                              # Wrapper for parsing and processing SharePoint files to markdown
├── main.py                                   # Central orchestrator: runs the full pipeline for a specified entity
├── requirements.txt                          # Python dependencies
├── LICENSE.txt
└── README.md
    - Brief overview of the use case
    - Instructions for setup, installation and usage
    - License and contact information
```

## Setup & installation

### Requirements

This use case relies on the following frameworks/libraries:
<br></br>

**Software & Frameworks**

* **Python 3.10**: Download from [python.org](https://www.python.org/).
* **OpenAI API**: Obtain an API key from [OpenAI](https://platform.openai.com/docs/overview).
* **Microsoft Graph API**: Access to a Microsoft/SharePoint environment.

Note: You must supply your own details for the SharePoint connection and Azure app registration (tenant ID, client ID, client secret, site/library info, etc.) - these are not included in the repository.

<br></br>
**Python Packages**

Install the necessary packages with:
```sh
pip install -r requirements.txt
```

### Installation

1. Clone the repo
```sh
git clone https://github.com/Regxelerator/solutions-use-case-library.git
```

2. Change the directory to the specific use case.
```sh
cd use_case_15
```

3. Configure the environment variables required for the SharePoint and LLM connections in your `.env` file:
```sh
OPENAI_API_KEY=YOUR_OPENAI_OR_AZURE_OPENAI_KEY
TENANT_ID=YOUR_AZURE_TENANT_ID
CLIENT_ID=YOUR_APP_CLIENT_ID
CLIENT_SECRET=YOUR_APP_CLIENT_SECRET
SITE_PATH_1=YOUR_SHAREPOINT_SITE_PATH
HOSTNAME=YOUR_SHAREPOINT_HOSTNAME
LIBRARY_NAME_SITE_PATH_1=YOUR_DOCUMENT_LIBRARY_NAME
LLM_PROVIDER=openai 
```

4. Update the document_requirements.json (your requirements checklist) /input directory before running the pipeline with your specific document requirements against which entity documents should be validated. For this use case, no example files are currently included; you must provide your own documents in SharePoint for testing.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

Run the main orchestration script with the following command, specifying the entity name (folder) to process (Note: this assumes that you use this repo to validate entity document submissions - for other applications, adjust the code accordingly):

```sh
python3 main.py run '<entity_name>' 
```
This will:
* Connect to SharePoint using your credentials and access the specified document library and entity folder.
* Extract files, metadata, and content, and generate intermediate JSONs.
* Validate the extracted documents against your requirements in input/document_requirements.json.
* Save validation results in the form of a Word document to the /output folder.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

In case of any issues or questions, please submit an issue here in the Repo or contact us at contact@regxelerator.com. 
For additional information about Regxelerator, visit www.regxelerator.com.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
