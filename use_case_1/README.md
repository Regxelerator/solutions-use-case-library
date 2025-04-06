# Use Case 1: Classifying Financial Consumer Complaints

## Overview

In this use case, we demonstrate how to harness large language models for classification tasks, using financial consumer complaints as an example. 
For authorities with a conduct and consumer protection mandate, collecting and analyzing consumer complaints is critical for detecting systemic issues, spotting emerging risks, and taking timely supervisory action, including early interventions. 
Classifying complaints by product and/or issue type is a fundamental step in this process. Large language models offer a robust alternative for text classification. 
By leveraging advanced contextual understanding and the ability to learn from minimal examples, it allows for a more nuanced and flexible classification of text such as consumer complaints.

In our practical demonstration, we illustrate how generative AI can be used to perform single-label classification of financial consumer complaints into one of eight predefined issue categories: advertising, account closure, application denial, customer service, disclosure, fees, fraud and loan repayment.

We present three different techniques for accomplishing this:
* Technique 1: Classification Using Few-Shot Prompting
* Technique 2: Classification Using Fine-Tuned Models
* Technique 3: Classification Using Vector Embeddings

For illustration purposes, we draw on a synthetic dataset of 500 financial consumer complaints, which were created by drawing on publicly disclosed complaint data. 
To highlight the effectiveness of the different techniques, we have manually assigned a category label to each complaint.  

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>

## Structure of the use case directory

```
use_case_1 (Classifying Financial Consumer Complaints)/
|___input/
    - file.json
├── retrieval/
│   ├── embedder.py       # Functions to convert text into high-dimensional vector embeddings.
│   └── retriever.py      # Functions to compute similarity (e.g., cosine) and retrieve most relevant segments for given requirements.
│
├── utils/
│   ├── pdf_parser.py     # Reads PDF files, extracts text, converts to Markdown, and segments into logical structured sections.
│   └── file_handler.py   # Identifies file type (PDF, DOCX, JSON), and delegates to appropriate parser (e.g., `pdf_parser.py`). Manages I/O.
│
├── llm/
│   └── llm_engine.py     # Handles prompt formatting and communicates with LLMs (e.g., GPT-4, Claude). Ensures output follows a structured schema (summary, assessment, score).
│
├── scripts/
├── main.py
│   - The orchestration script that executes the classification for the selected technique
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
cd use_case_1
```

3. Enter your OpenAI API in `.env`
```sh
OPEN_API_KEY='ENTER YOUR API';
```

4. Use the example input files or alternatively place your own files ```(Excel)``` into the ```input``` directory.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

Run the main orchestration script with the following commands:

1. Default operation: Classification via few-shot prompting
```sh
python main.py few-shot
```

2. Alternative 1: Classification via fine-tuning
```sh
python main.py fine-tuning
```

3. Alternative 2: Classification via vector embeddings
```sh
python main.py vector-embedding
```

The case will read data from the input files placed in the input folder and run classification technique on it. The output will be stored to the ```output directory``` 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

In case of any issues or questions, please submit an issue here in the Repo or contact us at contact@regxelerator.com. 
For additional information about Regxelerator, visit www.regxelerator.com.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
