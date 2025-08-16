# Use Case 18: Agentic Risk Incident Reporting Platform

## Overview

Use case 18 features a prototype for an agentic, interactive risk incident reporting platform to support the work of the risk management function at regulators. 
Instead of staff filling out a form, the platform relies on a conversational approach to capture information from the user about the risk incident, thereby ensuring that all information needs are met.  

The platform, which again combines a React frontend with a FastAPI backend, comprises two major components:

* An interactive chat pane where a risk incident agent engages in a proactive conversation with a platform user to capture risk incident information
* A structured risk incident reporting form which is updated in real-time as the conversation unfolds 

For the intake of a risk incident, the approach relies on two agents:
* An orchestration agent, responsible for obtaining from the user the basic information about the risk incident 
* A root cause specialist agent, tasked with engaging the user in a deep dive conversation about the root causes that led to the incident 

Both agents update the respective risk incident form fields with information from the user. 
With the chat pane and the risk incident form located side-by-side in the frontend, the user maintains full transparency into what is being captured and can through the dialogue with the agents correct information. 
Moreover, as an additional safeguard, the user must confirm the accuracy of the captured information 
prior to the submission of the final risk incident report. 

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library (coming soon)
<br></br>


## Structure of the use case directory

```

use_case_18/
│
├── frontend/                                   # React (Vite) application
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                          
│   └── src/
│       ├── App.jsx                             # 2-pane workspace
│       ├── api/
│       │   └── ws.js                           # WebSocket client -> FastAPI /agent/run
│       ├── components/
│       │   ├── ChatPane.jsx                    # Chat UI
│       │   └── IncidentForm.jsx                # Risk incident form UI
│       ├── store/
│       │   └── incident.js                     # Zustand store 
│       ├── theme/
│       │   └── muiTheme.js                     # MUI theme (incl. theme overides)
│       └── index.jsx                           
│
├── backend/                                    # FastAPI service
│   ├── app.py                                  # API entry-point (WS chat + /api/incidents/submit)
│   ├── draft_store.py                          # In-process draft + RFC-6902 JSON-Patch apply
│   └── risk_agents/
│       ├── agents_list.yaml                    # Agent definition
│       ├── agent_config_loader.py              # YAML loader
│       ├── context.py                          # Per-connection context
│       ├── schemas.py                          # Pydantic data model
│       ├── init.py                             
│       │                                       
│       ├── agent_library/                      # Agent library
│       │   ├── __init__.py                    
│       │   └── orchestrator_agent.py 
        │   └── root_cause_agent.py 
│       └── tools/                              # Agent tools
│           ├── __init__.py                     
│           └── incident_tools.py               
│
├── requirements.txt                            # Python dependencies (backend)
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
cd use_case_18
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
py -m uvicorn app:app --reload --port 8000

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
