# Use Case 3: Analyzing the Effctiveness of Board Meetings via Meeting Minutes

## Overview

In this use case, we demonstrate how generative AI can be applied to assess the effectiveness of board meetings through the analysis of board meeting minutes. For supervisors, understanding how board meetings are conducted in terms of attendance, agenda structure, and their overall effectiveness can yield valuable insights and complement broader governance effectiveness reviews. Our approach shows how generative AI can assist in transforming unstructured board meeting minutes into actionable insights for supervisors.

Our approach involves four key steps that starts with a structured extraction of the content of the meeting minutes followed by multiple steps of analysis. For our analysis, we apply common qualitative and quantitative governance effectiveness indicators. The results of the analysis are then synthesized in the form of a structured memo for supervisory review: 

* Step 1: Extracting the content of the meeting minutes and transforming it into structured data
* Step 2: Analyzing meeting attendance to evaluate patterns of board directors, key executives and other staff meeting participation
* Step 3: Assessing the nature and frequency of agenda items, complemented by an analysis of ancillary meeting effectiveness indicators
* Step 4: Synthesizing the results into a structured Word memo for review by supervisors

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>

## Structure of the use case directory

```
use_case_3/
|___input/
    - Use case specific input files (i.e. board meeting minutes)
├── utils/
│   ├── pdf_parser.py     # Reads PDF files and extracts their text
│   └── file_handler.py   # Identifies file type (PDF, DOCX, JSON), and delegates to appropriate parser (e.g., `pdf_parser.py`)
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
cd use_case_3
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