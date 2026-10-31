# MediCare AI | Context-Aware Medical Information Chatbot

**An AI-powered medical information assistant built with Flask, OpenAI GPT-4o-mini, JavaScript, and SQLite.**

MediCare AI is a personal AI engineering project developed to explore how conversational AI applications handle response streaming, prompt engineering, input validation, conversation history, context windows, and structured information extraction.

The application provides general medical information through a conversational interface. It is designed for educational purposes and is not a replacement for qualified healthcare professionals.

## Key Features

### AI-Powered Medical Conversations
- Uses OpenAI GPT-4o-mini for generating medical information responses.
- Uses a dedicated medical system prompt to guide response behavior.
- Supports follow-up questions using previous conversation context.
- Includes prompt-level restrictions to focus responses on healthcare topics.

### Real-Time Response Streaming
- Streams generated text using the OpenAI API.
- Uses Flask and Server-Sent Events (SSE) to deliver response chunks.
- Uses JavaScript to progressively display the generated answer.

### Input Validation and Error Handling
- Validates incoming JSON requests.
- Rejects invalid or empty messages.
- Applies a 2,000-character input limit.
- Handles API timeouts, connection errors, and rate limit errors.
- Uses `try`, `except`, and `finally` for error handling and database cleanup.

### Conversation History
- Stores conversations and messages using SQLite.
- Supports creating, viewing, and deleting conversations.
- Preserves completed conversations across application restarts.

### Token-Based Context Management
- Uses `tiktoken` to estimate token usage.
- Supports configurable context budgets.
- Selects recent complete conversation turns for model input.
- Reserves approximate token capacity for system instructions and generated responses.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend | Flask |
| LLM | OpenAI GPT-4o-mini |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| Streaming | Server-Sent Events |
| Token Counting | tiktoken |
| Structured Data Validation | Pydantic |
| Version Control | Git and GitHub |

## Application Architecture

```text
User
  |
  v
HTML / JavaScript Frontend
  |
  v
Flask API
  |
  +--> Input Validation
  |
  +--> SQLite Conversation History
  |
  +--> Context Manager
  |      |
  |      +--> Token Budget
  |      +--> Recent Conversation Turns
  |
  +--> Medical System Prompt
  |
  v
OpenAI GPT-4o-mini
  |
  v
Streaming Response (SSE)
  |
  +--> Save Completed Conversation
  |
  v
Frontend Displays Response
```

## Screenshots and Demonstration

**Welcome Screen**

<img width="1535" height="792" alt="image" src="https://github.com/user-attachments/assets/8901a182-7708-4f5e-8569-e317ca4b41cc" />


**Context-Aware Conversation**

<img width="1535" height="790" alt="image" src="https://github.com/user-attachments/assets/d55862e6-52c9-46da-b291-6a49ff434db4" />


**Medical Domain Restriction**

<img width="1535" height="786" alt="image" src="https://github.com/user-attachments/assets/57e7f93f-a389-40d7-a80e-e515c00f4a17" />


**Saved Chat History**

<img width="1535" height="790" alt="image" src="https://github.com/user-attachments/assets/09fb3db6-deac-48c6-8a61-ec2328aefb38" />


A short video demonstrating response streaming: Inside assets/


## Installation and Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/AanchalPandey16/Medical-ChatBot-.git
cd Medical-ChatBot-
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the API key

Create a `.env` file in the project root:

```env
OPENAI_KEY=your_openai_api_key_here
```

Never commit your actual API key.

### 5. Initialize the database

```bash
python database.py
```

### 6. Run the application

```bash
python app.py
```

Open the application locally at:

`http://127.0.0.1:8080`

An OpenAI API key with available usage is required.

## Experimental AI Engineering Modules

The repository also contains standalone learning experiments for:

- LLM-based medical information extraction.
- Pydantic structured output validation.
- User confirmation before saving extracted information.
- SQLite persistence for structured medical context.
- CRUD operations for individual medical facts.
- Conversation-specific memory retrieval.

These experiments demonstrate foundational concepts and are not yet fully integrated into the live chatbot.

## Current Limitations

- The application is currently intended for local development and demonstration.
- Medical responses are AI-generated and may be inaccurate or incomplete.
- Prompt-level domain restrictions do not guarantee complete medical safety.
- Conversation memory may omit older information when context budgets are applied.
- User authentication and production-grade privacy controls are not yet implemented.
- Structured medical memory is experimental.
- Semantic caching is not yet implemented.

## Future Improvements

- User-controlled persistent medical memory.
- Semantic FAQ retrieval using embeddings.
- Automated testing and evaluation.
- Improved emergency response handling.
- Authentication and conversation ownership.
- Secure deployment.

## Disclaimer

MediCare AI provides general educational health information only. It does not diagnose conditions, prescribe medication, or replace professional medical advice. For medical emergencies, seek immediate assistance from qualified emergency services.

Do not enter real patient records or sensitive personal health information into the demonstration version.

## Developer
**Aanchal Pandey**

Interested in AI Engineering, LLM applications, and building practical AI-powered systems.

[GitHub Repository](https://github.com/AanchalPandey16/Medical-ChatBot-)
