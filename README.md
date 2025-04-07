# Regxelerator's Generative AI Use Case Library

## Overview

Welcome to Regxelerator's generative AI use case library, a platform dedicated to showcasing opportunities for the application of generative AI by financial regulators in their daily operations. Throughout 2025, Regxelerator will be releasing a total of 50 worked examples that demonstrate how to apply generative AI for specific supervisory and regulatory tasks. Featuring varying levels of complexity, the use cases will provide a practical walkthrough complete with technical implementation details, including example prompts and Python scripts.

This repository serves as the technical companion to [Regxelerator's use case library](https://regxelerator.com/solutions/use-case-library). 
It provides the full source code and technical implementation details for each use case, enabling interested users to explore, adapt, and build upon the showcased workflows directly within their own environments.
<br></br>

## Structure of the use case directory

The repository is organized as a modular library, with each use case implemented in its own folder. Each folder contains:

* A dedicated README.md with use case-specific context
* Input data (public or synthetic)
* Modular scripts for each main step in the workflow
* Helper scripts such as for document processing, embedding and retrieval and LLM-specific components
* A main orchestration script (main.py) that runs the full pipeline as an end-to-end automated workflow

## Current use cases

* Use case 1: Classifying financial consumer complaints
* Use case 2: Assessing compliance of social media promotions
* Use case 3: Assessing the effectiveness of board meetings via meeting minutes
* Use case 4: Analyzing unstructured consultation feedback
* Use case 5: Performing basic comparative regulatory analysis
* Use case 6: Assessing compliance of outsourcing agreements
* Use case 7: Augmenting fit and proper reviews
* Use case 8: Synthesizing policy and research papers using agentic flows (beta)

## Setup & installation

### Requirements

Each use case lists its own setup steps in its respective folder. However, most use cases share common requirements:
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

For the general installation, follow these steps (adapted for the specific use case):

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
OPEN_API_KEY='ENTER YOUR API'
```

4. Use the example input files or alternatively place your own files into the ```input``` directory.
<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Data

All demonstrations rely exclusively on publicly available data sources and open databases. When necessary, we supplement these sources with AI-generated synthetic data to fill data gaps. 

## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

In case of any issues or questions, please submit an issue here in the Repo or contact us at contact@regxelerator.com. 
For additional information about Regxelerator, visit www.regxelerator.com.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Disclaimer

The approaches and techniques illustrated for each use case are intended to demonstrate potential applications of generative AI in financial supervision and regulation. They represent one of several possible methods and are not intended to prescribe best practices or comprehensive solutions. Adaptation and refinement will be necessary to align with specific supervisory objectives, regulatory frameworks, and data environments. Limitations in scope, data, or methodology may apply for demonstration purposes. Users are encouraged to consider additional steps - such as data preprocessing, contextual enrichment, and validation workflows - as appropriate to their own processes and to optimize the workflows for production.
