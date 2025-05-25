# Use Case 11: Fine-tuning for standardized meeting minute creation

## Overview

In this use case, we demonstrate how to leverage fine-tuning capabilities of large language models to automate and standardize the creation of structured meeting minutes from verbatim transcripts. Our example focuses specifically on monetary policy meetings, utilizing publicly available datasets of verbatim transcripts and associated finalized minutes released by the Bank of England as part of its transparency and accountability commitments. Given the nuanced and consistent nature of these official minutes, achieving equivalent standardization through traditional zero-shot or few-shot prompting methods can be challenging, making it a relevant candidate for fine-tuning."

We organize this demonstration into two primary parts. Part 1 involves the creation of the fine-tuned model while part 2 involves the application of the fine-tuned model to generate new meeting minutes: 
* Step 1A: Compiling and structuring the training dataset from the published transcripts and corresponding finalized minutes
* Step 1B: Processing this dataset to fine-tune a large language model
* Step 2A: Employing the fine-tuned model to process new, previously unseen transcripts
* Step 2B: Consolidating the sections of the minutes into a complete, formatted meeting minutes document in Word format

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>

## Structure of the use case directory

```
use_case_11/
|___input/
|   - Use case specific input files (i.e. meeting transcripts and minutes)
│
├── utils/
│   └── file_handler.py   # Handles certain file operations including preparation of the fine-tuning training dataset
│
├── llm/
│   └── llm_engine.py     # Handles prompt formatting and communication with LLMs
│
├── scripts/
│   - Scripts for the execution of individual steps
|
├── main_part_1_generate_finetuned_model.py
|   main_part_2_apply_finetuned_model.py
│   - The orchestration scripts that execute the steps under part 1 and part 2, respectively
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
cd use_case_11
```

3. Enter your OpenAI API in `.env`
```sh
OPENAI_API_KEY='ENTER YOUR API'
```

4. Use the example input files or alternatively place your own files ```(Excel)``` into the ```input``` directory.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

Run the main orchestration scripts with the following commands:

```sh
python3 main_part_1_generate_finetuned_model.py 
```

```sh
python3 main_part_2_apply_finetuned_model.py 
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

In case of any issues or questions, please submit an issue here in the Repo or contact us at contact@regxelerator.com. 
For additional information about Regxelerator, visit www.regxelerator.com.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
