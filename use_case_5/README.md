# Use Case 5: Performing Basic Comparative Regulatory Analysis

## Overview

In this use case, we explore how generative AI can facilitate regulatory benchmarking analysis. Comparative analysis of regulatory frameworks across jurisdictions is an essential input for various supervisory and policy-making activities, such as informing research, shaping an authority’s policy stance, or identifying critical regulatory gaps. By leveraging advanced reasoning capabilities inherent in large language models, we demonstrate an automated approach to systematically analyze and benchmark regulations from different jurisdictions on a specific topic.

We structure our approach into four steps as follows: 

* Step 1: Extracting regulatory texts and converting them into structured representations through a tailored segmentation approach.
* Step 2: Establishing a benchmarking framework by identifying relevant analytical dimensions and mapping regulatory content from each jurisdiction accordingly.
* Step 3: Conducting a comparative analysis across jurisdictions for each identified benchmarking dimension.
* Step 4: Consolidating the benchmarking insights into a structured Word document to facilitate supervisory review and decision-making.

Our methodology for this use case is exploratory in nature: rather than feeding the model with a predefined benchmarking framework or extensive contextual guidance, we rely on the generative AI model’s reasoning capabilities to identify suitable benchmarking dimensions on the basis of the regulatory texts.

For the demonstration we apply this approach to crowdfunding regulations from two emerging market jurisdictions.


For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>

## Structure of the use case directory

```
use_case_5/
|___input/
    - Use case specific input files (i.e. crowdfunding regulations)
│
├── utils/
│   ├── pdf_parser.py     # Reads PDF files and extracts their text
│   └── file_handler.py   # Identifies file type (PDF, DOCX, JSON), delegates to appropriate parser (e.g., `pdf_parser.py`), and handles other basic file operations
│
├── llm/
│   └── llm_engine.py     # Handles prompt formatting and communicates with LLMs (e.g., GPT-4, Claude). Ensures output follows a structured schema (summary, assessment, score).
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
cd use_case_5
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
