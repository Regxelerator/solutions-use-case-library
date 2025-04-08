# Use Case 2: Assessing Compliance of Social Media Promotions

## Overview

In focus of this use case is how to leverage large language models’ vision and reasoning capabilities to assess the compliance of social media promotions with applicable financial promotion rules. As social media becomes an increasingly prevalent channel for financial advertising, effective monitoring and supervision of these promotions is essential to ensure consumer protection and maintain market integrity. Our objective is to show how generative AI can assist supervisors in identifying potential gaps or instances of non-compliance.

To illustrate this approach, we focus on a sample of static Facebook advertisements published by financial institutions in developing countries, sourced from Meta’s Ad Library. Each advertisement consists of post text accompanied by a visual element promoting a financial product or offer. Leveraging the multimodal capabilities of generative AI, we assess these ads against a consolidated set of financial promotion rules, which are derived from actual regulatory requirements issued by leading financial authorities and articulated in the form of principles.

For the purpose of the walkthrough, we break the technical implementation into three steps:

* Step 1: Extracting content and visual characteristics of the promotion as a foundation for the analysis
* Step 2: Analyzing the extracted content vis-à-vis the defined financial promotion rules
* Step 3: Consolidating and prioritizing the compliance analysis results for further supervisory review


For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>

## Structure of the use case directory

```
use_case_2/
│
|___input/    - Use case specific input files (i.e. example social media promotions)
│
├── utils/
│   └── file_handler.py   # Handles certain file operations
│
├── llm/
│   └── llm_engine.py     # Handles prompt formatting and communicates with LLMs (e.g., GPT-4, Claude). Ensures output follows a structured schema (summary, assessment, score).
│
├── scripts/
│   - Scripts for the individual steps
│
├── main.py
│   - The orchestration script that:
│     - Executes all steps end-to-end (Steps 1–3)
│     - Produces final Excel report/documentation
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
cd use_case_2
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