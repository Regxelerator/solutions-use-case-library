# Use Case 10: Leveraging web search tools to support entity-specific OSINT searches

## Overview

In this use case, we introduce an example of an agentic workflow that leverages web search tools to identify adverse news item about an entity and its key position holders - a common process frequently executed by authorities as part of open source intelligence (OSINT) searches during ongoing supervision and/or the licensing stage. 

Our workflow involves four steps, each executed by a dedicated agent:
* Step 1: Creating tailored search queries for a given entity. 
* Step 2: Executing news search based on the custom queries and filtering news for adverse information.
* Step 3: Validating adverse findings and enriching them with further information.
* Step 4: Consolidating findings for further supervisory review. 

For testing purposes, we make available a template that interested users can populate with entity-specific information and execute their own searches. 

The tools demonstrated in our example workflow rely entirely on the Bing Search API, which provides a legal and officially authorized means of retrieving and processing web search data. Beyond these, we are in the process of exploring other options such as the use of computer use tools for use in an OSINT context and will share examples of their application as part of this or a dedicated new use case in the near future. 

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>

## Structure of the use case directory

```
use_case_10/
|___input/
    - Use case specific input files (i.e. YAML files with entity specific information)
│
├── llm/
│   └── llm_engine.py     # Handles prompt formatting and communication with LLMs.
│
├── scripts/
│   - Scripts for the four individual agentic modules
│
├── main.py
│   - The orchestration script that:
│     - Executes all agents end-to-end (Steps 1–4)
│     - Produces the final memo with findings
│
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
* **Bing Search API**: Obtain an API key from [Azure]([https://www.microsoft.com/en-us/bing/apis/bing-web-search-api]).

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
cd use_case_10
```

3. Enter your OpenAI API in `.env`
```sh
OPEN_API_KEY='ENTER YOUR API Key'
BING_API_KEY='ENTER YOUR API Key'
```

4. Populate the template in the folder ```entity_files``` in the ```input``` directory with entity-specific information. Relabel the template with the entity name.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

Run the main orchestration script with the following command:

```sh
python3 main.py 
```

The case will read data from the input files placed in the input folder and run the code. The output will be stored to the ```output directory``` 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

In case of any issues or questions, please submit an issue here in the Repo or contact us at contact@regxelerator.com. 
For additional information about Regxelerator, visit www.regxelerator.com.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Disclaimer

The approaches and techniques illustrated in this use case are intended to demonstrate potential applications of generative AI in financial supervision and regulation. They represent one of several possible methods and are not intended to prescribe best practices or comprehensive solutions. Adaptation and refinement will be necessary to align with specific supervisory objectives, regulatory frameworks, and data environments. Limitations in scope, data, or methodology may apply for demonstration purposes. Users are encouraged to consider additional steps - such as data preprocessing, contextual enrichment, and validation workflows - as appropriate to their own use cases and to optimize the workflows for production.
