# Use Case 12: Realtime Virtual Meeting Advisor

## Overview

In this use case, we introduce a “Realtime Virtual Meeting Advisor” that assists financial supervisors by capturing and transcribing live virtual discussions/meetings with (licensed) entities and generating in realtime targeted follow-up questions to guide the conversation.

At the center of our prototype are three core modules which are operated in parallel: 

* Module 1 - Audio capture & transcription: Recording microphone input via pyaudiowpatch, streaming it to OpenAI’s real-time transcription WebSocket (gpt-4o-transcribe), and aggregating completed speech turns into a running transcript

* Module 2 - Question generation: Feeding the transcript in defined intervals to the LLM to generate targeted deep dive questions and as part of that extracting relevant content from previously uploaded entity files through vector search to enrich the question generation process

* Module 3 - Live UI rendering: Displaying both the conversation and the follow-up questions in a dedicated interface as the conversation unfolds


For the purpose of our demonstration, we simulate a (simplified) conversation between a regulator and a licensed entity to discuss the entity's cyber risk management framework and controls using a generative AI created conversation script and upload an example IT security policy to the vector store. Interested users can however apply the tool to any other (live) audio and files.

For additional information about the workflow and the individual steps, please visit Regxelerator's use case library: https://regxelerator.com/solutions/use-case-library
<br></br>


## Structure of the use case directory

```

use_case_12/
|___input/
|   - Optional inputs (e.g. audio snippets for testing, input files for vector store)
│
├── output/
│   - Transcripts, logs 
│
├── llm/
│   └── llm_engine.py           # Handles communication with LLMs
│       
│
├── ui/
│   └── popup.py                # CustomTkinter pop-up window 
│    
│
├── audio/
│   └── recorder.py             # Handles audio recording, streams mic audio to the OpenAI websocket, writes JSON transcripts, and enqueues them  
│      
│
├── workers/
│   ├── transcript_updater.py   # Manages realtime transcription and update of UI with transcript
│   │    
│   └── commentator.py          # Handles interaction with llm_engine to identify follow-up questions in defined time intervals
│        
│
├── utils/
│   ├── logger.py               # Logs OpenAI API calls 
│   │    
│   └── constants.py            # Documents relevant constants including model names, intervals, file paths, env loading
│    
│
├── main.py                     # Central orchestrator
│   
|
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
cd use_case_12
```

3. Enter your OpenAI API and the OpenAI Vector Store ID (once created) in `.env`
```sh
OPENAI_API_KEY='ENTER YOUR API'
VECTOR_STORE_IDS='ENTER YOUR VECTOR_STORE_ID'
```

4. After initiating the main.py, simply start a meeting or play a test audio file simulating a conversation for the recording and the other actions to start.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

Run the main orchestration scripts with the following commands:

```sh
python3 main.py 
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

In case of any issues or questions, please submit an issue here in the Repo or contact us at contact@regxelerator.com. 
For additional information about Regxelerator, visit www.regxelerator.com.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
