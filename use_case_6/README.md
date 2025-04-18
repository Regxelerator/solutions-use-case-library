# Use Case 6: Assessing Compliance of Outsourcing Agreements

## Overview

In this use case, we revisit the application of generative AI for compliance assessment, demonstrating how large language models can be leveraged to evaluate outsourcing agreements against predefined regulatory content requirements. With operational resilience increasingly prioritized by regulators, the scrutiny of outsourcing arrangements—both at the licensing stage and throughout ongoing supervision—is expected to gain further prominence. Given the typically extensive length and complexity of outsourcing agreements, their review represents a particularly compelling scenario for technological innovation.

For the purpose of this worked example, we break down the process into six logical steps:

* Step 1: Translating regulatory requirements for outsourcing agreement content into a structured, machine-readable inventory
* Step 2: Segmenting the outsourcing agreement into logical, analyzable units using a custom segmentation approach
* Step 3: Generating vector embeddings for both the segmented contract texts and structured regulatory requirements to enable semantic analysis
* Step 4: Mapping contract provisions to regulatory requirements through embeddings-based similarity search
* Step 5: Assessing compliance by comparing contract provisions against the regulatory content requirements
* Step 6: Consolidating the assessment results into a structured document optimized for supervisory review

For the demonstration, we utilize a publicly disclosed, 70-page IT outsourcing agreement from the U.S. Securities and Exchange Commission’s EDGAR database, filed by a financial institution as part of its 8-K submission and a composite set of regulatory requirements, synthesized from actual outsourcing guidelines issued by leading international supervisory authorities.

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>

## Structure of the use case directory

```
use_case_6/
|___input/
    - Use case specific input files (i.e. example outsourcing agreement)
├── retrieval/
│   ├── embedder.py       # Functions to convert text into high-dimensional vector embeddings.
│
├── utils/
│   ├── pdf_parser.py     # Reads PDF files, extracts text, and converts text to Markdown
│   └── file_handler.py   # Multiple functions to read and write to JSON files and to create the Word report
│
├── llm/
│   └── llm_engine.py     # Handles prompt formatting and communication with LLMs.
│
├── scripts/
│   - Scripts for the six individual worksteps
│
├── main.py
│   - The orchestration script that:
│     - Executes all steps end-to-end (Steps 1–6)
│     - Produces the final output report in Word
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
cd use_case_6
```

3. Enter your OpenAI API in `.env`
```sh
OPEN_API_KEY='ENTER YOUR API';
```

4. Use the example input files or alternatively place your own files ```(Excel)``` into the ```input``` directory.
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
