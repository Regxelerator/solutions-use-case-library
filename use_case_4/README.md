# Use Case 4: Analyzing Unstructured Consultation Feedback

## Overview

In this use case we explore the application of large language models to streamline the analysis of unstructured feedback from consultation papers. For policymakers, understanding the full range of stakeholder input is essential—but manually reviewing diverse and lengthy text-based submissions can be both time-consuming and resource-intensive. By integrating large language models with traditional programming, we show how to efficiently parse, segment, and synthesize varied feedback into structured insights that can inform policymaking decisions. 

Our approach relies on four consecutive steps as follows: 

* Step 1: Identifying and organizing key details from the consultation paper and its questions to set a structured foundation for analysis.
* Step 2: Systematically extracting responses, segmenting them logically, and mapping them to the relevant consultation questions.
* Step 3: Synthesizing the responses to generate insights and highlight recommendations based on stakeholder feedback
* Step 4: Compiling the insights into a summary report, supplemented by a more detailed Excel file that allows filtering of feedback by respondent and question.

For the demonstration, we utilize the Financial Stability Board’s consultation paper titled "Enhancing Third-Party Risk Management and Oversight: A Toolkit for Financial Institutions and Financial Authorities" along with the 23 publicly available organizational responses submitted as part of the consultation process.

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>

## Structure of the use case directory

```
use_case_4/
|___input/
    - Use case specific input files (i.e. consultation paper and consultation responses)
├── utils/
│   ├── pdf_parser.py     # Reads PDF files and extracts their text
│   └── file_handler.py   # Identifies file type (PDF, DOCX, JSON), delegates to appropriate parser (e.g., `pdf_parser.py`), and handles other basic file operations
│
├── llm/
│   └── llm_engine.py     # Handles prompt formatting and communication with LLMs.
│
├── scripts/
├── main.py
│   - The orchestration script that:
│     - Executes all steps end-to-end (Steps 1–4)
│     - Produces final Word report
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
cd use_case_4
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