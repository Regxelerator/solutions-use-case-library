# Use Case 13: Analyzing non-financial disclosures in XBRL filings

## Overview

In this use case, we demonstrate how to develop a large language model (LLM)-augmented pipeline for analyzing non-financial disclosures contained in structured XBRL filings. Regulatory authorities and standard setters continue to emphasize the adoption of XBRL as a standard for both financial and non-financial regulatory reporting, enabling machine-readability and efficient downstream processing. Recent initiatives such as the Financial Stability Board’s release of the its final Format for Incident Reporting Exchange (FIRE), published in April 2025, have further expanded the use of dedicated XBRL taxonomies for non-financial information. As [recognized by the XBRL community](https://www.xbrl.org/a-getting-started-guide-experimenting-with-llms-for-xbrl-analysis/), LLMs offer significant potential for enhancing the analysis of disclosures reported in XBRL format.

Our workflow is organized into four consecutive steps:
* Step 1: Mapping XBRL concepts to regulatory requirements.
* Step 2: Extracting and converting relevant non-financial disclosures from XBRL filings.
* Step 3: Performing analysis to derive insights from the extracted information.
* Step 4: Documenting key insights in a supervisor-friendly memo. 

We illustrate the approach using the U.S. Securities and Exchange Commission’s new XBRL taxonomy for cyber security disclosures, applied to a sample set of ten state commercial banks as part of their 2024 year-end 10-K filings (publicly accessible via the EDGAR database). 

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>

## Structure of the use case directory

```
use_case_13/
|___input/
    - Use case specific input files (i.e. XBRL instance files, taxonomy mapping)
│
├── llm/
│   └── llm_engine.py     # Handles prompt formatting and communication with LLMs.
│
├── scripts/
│   - Scripts for the four individual agentic modules
│
├── main.py
│   - The orchestration script that:
│     - Executes all individual scripts (Steps 1–4)
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
cd use_case_13
```

3. Enter your OpenAI API in `.env`
```sh
OPEN_API_KEY='ENTER YOUR API Key'
```

4. Use the example input files in the folder ```entity_filings``` and the example taxonomy in the folder ```taxonomy``` in the ```input``` directory or alternatively place your own files in the folders.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

Run the main orchestration script with the following command:

```sh
python3 main.py 
```

The script will read data from the input files placed in the input folder and run the code. The output will be stored to the ```output directory```

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
