# Use Case 16: Briefing Memo Creator (Basic) 

## Overview

In this prototype app, we demonstrate how a large‑language‑model (LLM) powered workflow can streamline the end‑to‑end creation of internal briefing memos, such as for certain committee meetings or other routine reporting exercises. The showcased app combines a React + Material‑UI front‑end with a FastAPI back‑end. Unlike other use cases, which are designed as fully automated workflows, this app involves an interactive human-LLM interaction.

The workflow comprises three principal steps:

* Step 1: Uploading internal or external content into the app including automatic content and metadata extraction
* Step 2: Generating and editing individual sections of the memo through LLM-powered content generation and editing via LLM presets and/or custom instructions
* Step 3: Previewing the draft memo and exporting it as fully formatted Word or PDF file for further editing and/or distribution

Additionally, an administration tab offers the ability to directly edit existing and add new presets (i.e. pre-defined prompts for content generation and editing) via the frontend. 

For this use case, no sample input files or requirements are provided. Users can upload their own internal or external documents via the frontend when testing the application.

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library.
For a more advanced implementation of the memo creator, refer to companion Use Case 17.
<br></br>


## Structure of the use case directory

```

use_case_16/
│
├── frontend/                                   # React (Vite) application
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── App.jsx                             # 4‑tab workspace
│       ├── theme/                              # MUI theme
│       ├── components/
│       │   ├── UploadTable.jsx                 # Implementation of table for the display of uploaded content
│       │   └── tabs/                           # Tab1‑Tab4 implementations
│       └── index.jsx
│
├── backend/                                    # FastAPI service
│   ├── app.py                                  # API entry‑point
│   ├── extractors.py                           # File‑type parsers
│   ├── url_fetch.py                            # Remote HTML/PDF fetcher
│   ├── llm.py                                  # OpenAI helpers & logging
│   ├── converters.py                           # Markdown→DOCX/PDF
│   ├── content_store.py                        # Master content list (JSON)
│   ├── memo_store.py                           # Section persistence (JSON)
│   ├── preset_store.py                         # Prompt preset storage
│   └── prompts/
│       └── PROMPT_METADATA_EXTRACTION.txt      # Prompt for metadata extraction
│
├── uploads/                                    # Auto‑created; holds raw files
├── memo_sections.json                          # Generated memo data
├── presets.json                                # Generated/edited presets
├── requirements.txt                            # Python dependencies
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
* **Node.js ≥ 18 LTS**
* **Pandoc** (optional)
* **Node.js ≥ 18 LTS**


Note: You must supply your own details for the SharePoint connection and Azure app registration (tenant ID, client ID, client secret, site/library info, etc.) - these are not included in the repository.

<br></br>
**Python Packages**

Install the necessary backend dependencies:
```sh
pip install -r backend/requirements.txt
```

### Installation

1. Clone the repo
```sh
git clone https://github.com/Regxelerator/solutions-use-case-library.git
```

2. Change the directory to the specific use case.
```sh
cd use_case_16
```

3. Configure the environment variables required for the LLM connections in your `.env` file:
```sh
OPENAI_API_KEY=YOUR_OPENAI_OR_AZURE_OPENAI_KEY

```

4. Optional: Update the presets as required to tailor to the specific area of application.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

Run the application as follows:

```sh
cd backend
uvicorn app:app --reload --port 8000

cd frontend
npm run dev     

```
By default the front‑end proxies API calls to http://localhost:8000/api (configured in vite.config.js).
For details on the detailed workflow, please refer to the case study narrative on the website. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

In case of any issues or questions, please submit an issue here in the Repo or contact us at contact@regxelerator.com. 
For additional information about Regxelerator, visit www.regxelerator.com.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
