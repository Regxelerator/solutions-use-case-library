# Use Case 8: Synthesizing Policy & Research Papers with Agentic Flows (Beta)

## Overview

In this use case introduce a prototype for a workflow that leverages agentic modules, demonstrating how specialized agents can effectively synthesize insights from multiple policy and research papers into a cohesive thematic report. Supervisors and policymakers frequently face the challenge of distilling actionable insights from extensive and diverse sets of documents. By employing generative AI agents, we illustrate an efficient approach to systematically analyze, structure, and consolidate complex information into a clear and comprehensive synthesis.

We structure this workflow into seven sequential steps, each executed by a specialized agent:
* Step 1: Pre-processing the collected reports by extracting their textual content and relevant metadata.
* Step 2: Segmenting and uploading the extracted report content into a vector store to facilitate semantic analysis.
* Step 3: Performing semantic search to identify and retrieve the most relevant content segments from each report.
* Step 4: Creating a structured report outline through an interactive exchange between specialized agents.
* Step 5: Mapping the identified relevant content segments to the established report outline.
* Step 6: Composing and iteratively reviewing the detailed synthesis report through a dual-agent interaction model.
* Step 7: Generating and finalizing the structured synthesis report for supervisory and policy review.

For demonstration purposes, we utilize a curated collection of ten recent reports (published in 2024 and 2025) from global standard setters and national authorities, each addressing various aspects of artificial intelligence in financial services, regulation, and supervision and produce a synthesis report on the topic of supervision of AI in financial services, which is fully grounded in the selected source materials.

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>

## Structure of the use case directory

```
use_case_8/
|___input/
    - file.json
├── retrieval/
│   ├── embedder.py       # Functions to upload extracted text to a vector store.
│   └── retriever.py      # Functions to perform vector store operations including listing and searching files
│
├── utils/
│   ├── pdf_parser.py     # Reads PDF files, extracts text, converts to Markdown, and segments into logical structured sections.
│   └── file_handler.py   # Multiple functions to read and write to JSON files and to create the Word report
│
├── llm/
│   └── llm_engine.py     # Handles prompt formatting and communicates with LLMs (e.g., GPT-4, Claude). Ensures output follows a structured schema (summary, assessment, score).
│
├── scripts/
│   - Scripts for the seven individual agentic modules
│
├── main.py
│   - The orchestration script that:
│     - Executes all steps end-to-end (Steps 1–7)
│     - Produces the final synthesis report in Word
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
cd use_case_8
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