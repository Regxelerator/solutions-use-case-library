# Use Case 17: Briefing Memo Creator (Agentic) 

## Overview

This prototype builds on Use Case 16, which introduced a large-language-model (LLM)-powered workflow for streamlining the end-to-end creation of internal briefing memos—such as those prepared for committee meetings or other recurring reporting tasks. In contrast to the more basic, primarily user-driven process under Use Case 16, this version introduces two agentic modules: one for memo creation and another for revising the draft based on user feedback. This approach significantly reduces the user’s workload while preserving meaningful user interaction. 

As before, the showcased app combines a React + Material-UI front end with a FastAPI back end.

The workflow also here is broken down into three main steps:

* Step 1: Uploading internal or external content into the app, with automated content and metadata extraction (as in Use Case 16)
* Step 2: Generating individual sections of the memo via an agentic workflow based on uploaded content and initial user instructions
* Step 3: Revising the draft memo through a separate agentic workflow, automatically incorporating user feedback (coming soon)

To illustrate the tool in practice, the prototype includes a demonstration scenario involving a briefing memo for the international affairs department of a regulatory authority.

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
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
│       │   └── tabs/                           # Tab1‑Tab3 implementations
│       └── index.jsx
│
├── backend/                                    # FastAPI service
│   ├── app.py                                  # API entry‑point
│   ├── agentic_flow.py                         # Runs multi‑agent workflow
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
├── agentic_flow_memo_creation/                 # Agent‑specific code for the memo creation agentic module
│   ├── __init__.py                             # Module alias helper
│   ├── agent_config_loader.py                  # YAML loader
│   ├── agents_list.yaml                        # Declarative agent roster
│   ├── schemas.py                              # Pydantic data models
│   │
│   ├── agent_library/                          # Agent factory layer
│   │   ├── __init__.py
│   │   ├── planner_agent.py
│   │   ├── outline_agent.py
│   │   ├── section_writer_agent.py
│   │   ├── section_orchestrator_agent.py
│   │   └── critic_agent.py
│   │
│   └── tools/                                  # Agent tools
│       ├── __init__.py
│       ├── content_loader.py
│       ├── content_metadata_loader.py
│       └── critic_tool.py
│
├── agentic_flow_feedback_integration/          # Agent‑specific code for the revision of the memo based on user feedback (to come)
│
├── uploads/                                    # Auto‑created; holds raw files
├── memo_sections.json                          # Generated memo data
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
cd use_case_17
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
