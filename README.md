# My Assistant 

### Overview

My Assistant is a powerful tool that leverages OpenAI's APIs and a Language Learning Model (LLM) to perform function calls. It allows the LLM to interact with external systems via API calls, enabling the execution of various tools and commands. 


## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.10
- [MiniConda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution) (for managing environments and dependencies)
- [Docker](https://www.docker.com/products/docker-desktop/)

### Setup

1. **Install MiniConda** (if not already installed):

   Follow the instructions on the [official MiniConda page](https://docs.conda.io/en/latest/miniconda.html) to download and install MiniConda for your operating system.

2. **Create a Conda Environment**:

   After installing MiniConda, create a new environment for the project:

   ```shell
   conda create --name my_assistant python=3.10
   ```

   This environment will be specifically for running the tools in this repository.

3. **Activate the Environment**:

   Activate the newly created environment:

   ```shell
   conda activate my_assistant
   ```

4. **Install Dependencies**:

   Install necessary Python packages within your Conda environment:

   ```shell
   pip install -r ./src/requirements.txt
   ```

5. **Create .env file**:
   
   Contains all application environment variables. If you need a key, then @ a contributor
   ```shell
   cp -rf .env.example .env
   ```

## Usage

Run a local environment (requires online connection for external APIs)
```bash
$ docker-compose -f docker-compose.yml up --build
```

Example: Command Execution
```bash
curl --location 'http://127.0.0.1:8000/command/execute' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjRiNTVmZDhjNzJmMTY2ODU5ZTIxYTQ1OWE1MjFmNzJlYTcyODliNmM0NTRiY2Y1M2RmY2FjOTFmY2EyMDk3YzQwMmJhZmE4MjJkYjdkYjI4In0.eyJhdWQiOiI4OTI1NDEiLCJqdGkiOiI0YjU1ZmQ4YzcyZjE2Njg1OWUyMWE0NTlhNTIxZjcyZWE3Mjg5YjZjNDU0YmNmNTNkZmNhYzkxZmNhMjA5N2M0MDJiYWZhODIyZGI3ZGIyOCIsImlhdCI6MTcwODExOTU5OCwibmJmIjoxNzA4MTE5NTk4LCJleHAiOjE3MDgxMjA0OTgsInN1YiI6IjgwNTEyMjIiLCJzY29wZXMiOltdfQ.LhHobddCix0ffw-WdxP_PbFmtjM7-ubu69dCudy9JNujIfCziFv7DO_J0kGT_LGosUUsbe5WCnWrRd6IRsvz4oP3BcHOMs5yrPSfLkM4c7nslrpqqzJ_Cts5fKJ8FHjz_UNZW4mWqP2riaJYgu--zG0WwxTxRYBX2XsvjW4_6w3MP0Fmr9WcZxzZO02jsGFZQRVAoFYNLytUwTR1i9tRc5LMM3BhTvSL9oq6ZNRUXNose1y4amKSPXU_1xUD1OdeCEn-ttAako-KWukeQLo5pxXcYhAaLwI_i-mhFDHe1R8jSEnoINHetoYyJud7V5aWvuABvsZb0fiGJlansBLRkfe7zndXhaKmiYiFiz_AtYDb3jUBx91sv3Q_Ex799i8zVYx-4LM6HBaCnCWW5buC_UaBl_Bejj3hv-nE-YmhZc_UrMntR5CNegswSp5A55wJkThbFo9BTyX90IH0eS-nUTkd-pNKPXcPtCHcvvqodEy6Ar6zGPrV_HwFYqxZFRl0jCJU7TtptTbii1kgZTgoZmQQNjX7lThTJIfZTq1sq6yT88tJti5p5PKws847DUUA4ilDboVV_1zZmPJKN6-dY-lCNrKIISFIrFdRpy0RK1BgvVGq9pD2ZpiDd-uxUpJum2TV8gimRySBsbIjDzLkIFzaLQYKzv-ZJdA5A0YNpqM' \
--data '{ 
   "command": "change my collection time to 15 mins"
}'
```
`Authorization: Bearer` must contain a `sub` 

## Local Debugging (vscode)
```bash
$ docker-compose build
$ docker-compose up
```
(Shortcut F5) Open VSCode > Debugger > Run 


## Running Tests
```bash
$ cd ./src/tools/{tool_name}/tests
$ pytest
```
 
For parallel execution and reporting
```bash
$ pytest -n auto test_process_speak_to_agent.py --html=pytest_report.html
```

