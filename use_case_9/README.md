# Use Case 9: Performing comparative risk analysis based on annual report MD&A information

## Overview

In this use case we show how to leverage large language models to extract and review risk information covered in financial firm's annual reports. Public risk disclosure information such as those in the narrative-heavy Management Discussion & Analysis (MD&A) section of an annual report including year-on-year changes in risk narratives forms an important input into supervisory review processes. Our approach involves a bespoke generative AI-assisted methodology for breaking down the lengthy MD&A section into its constituent chapters and then systematically extract, synthesize and analyse relevant risk information - illustrated using the example of cyber risk - across two consecutive reporting periods and turn it into a structured output for further review by supervisors. 

Our workflow involves seven consecutive steps:

* Step 1: Converting annual report PDFs into HTML to enable downstream text processing
* Step 2: Identifying MD&A section boundaries by detecting and extracting its table of contents and associated html anchors
* Step 3: Splitting the MD&A HTML into discrete chapter segments based on the identified section markers
* Step 4: Filtering MD&A segments for relevant risk content through a hybrid keyword and semantic search
* Step 5: Extracting detailed risk information by section and synthesizing information into a holistic narrative
* Step 6: Performing a comparative analysis of the synthesized risk information across two consecutive years
* Step 7: Generating a consolidated, formatted comparative risk analysis report optimized for supervisory review

Our test demonstration uses as input the 2023 and 2024 full annual reports from three large Canadian banks. 

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library

## Structure of the use case directory

```
use_case_9/
|___input/
    - Use case specific input files (i.e. example outsourcing agreement)
├── retrieval/
│   ├── embedder.py       # Functions to convert text into high-dimensional vector embeddings.
│
├── utils/
│   └── file_handler.py   # Multiple functions to read and write to JSON files
│
├── llm/
│   └── llm_engine.py     # Handles prompt formatting and communication with LLMs.
│
├── scripts/
│   - Scripts for the seven individudal steps of the workflow
│
├── main.py
│   - The orchestration script that:
│     - Executes all steps end-to-end (Steps 1–7)
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
* **Poppler**: Download from [GitHub](https://github.com/oschwartz10612/poppler-windows/releases/tag/v24.08.0-0) - 

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
cd use_case_9
```

3. Enter your OpenAI API in `.env`
```sh
OPEN_API_KEY='ENTER YOUR API'
```

4. Install Poppler and insert the path to insert path to pdftohtml.exe in `main.py`
```sh
PDFTOHTML_PATH = r"REPLACE BY ACTUAL PATH"
```

5. Use the example input files or alternatively place your own files ```(PDF)``` into the ```input``` directory.
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
