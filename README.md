# SLR Paper Writer Agent

An autonomous agent that performs Systematic Literature Reviews (SLR) and writes academic papers based on the PRISMA 2020 guidelines.

## Features
- **Automated Search**: Semantic Scholar & arXiv integration.
- **Snowballing**: Forward and backward citation chasing.
- **LLM Screening**: Chain-of-Thought screening based on inclusion/exclusion criteria.
- **Data Extraction**: Structured extraction of methodology, improvements, and quality (AMSTAR 2 Lite).
- **Analysis**: Automatic generation of PRISMA diagrams, comparison tables, and GRADE assessments.
- **Writing**: Generates a full academic paper (Introduction -> Conclusion).
- **Review**: Iterative self-correction loop using an MCP-based reviewer.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Jnooo-cloud/SLR-PAPER-WRITER.git
   cd SLR-PAPER-WRITER
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up API Keys:
   Create a `.env` file in the `literature_autopilot` directory:
   ```bash
   GEMINI_API_KEY=your_key_here
   SEMANTIC_SCHOLAR_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here (optional, if using OpenAI for screening)
   ```

## How to Use for YOUR Topic

The system is designed to be easily adaptable to any research topic.

### 1. Configure the Topic (`config.yaml`)
Edit `literature_autopilot/config.yaml`:
- **`slr_topic`**: Your research topic.
- **`search.keywords`**: Keywords for the search APIs.
- **`search.seed_urls` / `seed_titles`**: Known relevant papers to start snowballing.
- **`paper_structure.sections`**: Define the sections of your final paper.

### 2. Customize Prompts (`prompts/`)
The logic for screening and extraction is defined in the prompt files in `literature_autopilot/prompts/`. You **MUST** update these for your topic.

- **`screening_prompt.md`**: 
  - Update the **Research Question**.
  - Update the **Inclusion/Exclusion Criteria**.
  - Update the **PICO Framework** definitions.
  - Update the **Examples** (optional but recommended).

- **`prescreening_prompt.md`**:
  - A shorter version of the screening criteria for the initial pass. Update criteria here too.

- **`extraction_prompt.md`**:
  - Update the **Research Question**.
  - Update the **Data Extraction Fields** (e.g., if you are not comparing "Methodological Differences", change the JSON schema instructions).
  - Update **Quality Assessment** questions if needed.

### 3. Run the Agent
```bash
python3 literature_autopilot/slr_bot.py --screen --download-pdfs --extract-data --write-paper --final-review
```

## Project Structure
- `literature_autopilot/`
  - `config.yaml`: Main configuration.
  - `prompts/`: Markdown files containing LLM prompts.
  - `pipeline.py`: Main orchestration logic.
  - `slr_bot.py`: CLI entry point.
  - `...`: Other modules (search, screen, extract, etc.).
