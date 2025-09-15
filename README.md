Class-schedule-QA Bot
=====================

This bot continuously generates questions, sends them to a GPT model, evaluates responses for security issues, grammar quality, and compliance with university AI guidelines, and computes an overall rating.

Quickstart
----------

1. Ensure dependencies are installed from the project root:

```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key (uses the same config mechanism as `src/config.py`). For convenience, export the environment variable:

```bash
export OPENAI_API_KEY=sk-... 
```

3. Adjust `guidelines.json` as needed for your university policies.

4. Run the bot loop:

```bash
python -m Class-schedule-QA.runner
```

Files
-----

- `question_generator.py`: Creates diverse prompts for testing.
- `grammar.py`: Simple grammar/quality scoring using TextBlob.
- `guidelines.py`: Loads and evaluates guideline rules.
- `security_wrapper.py`: Reuses existing `src/security_analyzer.py` for checks.
- `rater.py`: Combines scores into an overall rating.
- `runner.py`: Main loop sending to GPT and logging results.
- `guidelines.json`: Example guideline rules and scoring config.

Notes
-----

- This folder is self-contained but leverages the existing `src` package for OpenAI client config and security checks.
- Logs print to stdout; you can adapt to DB by plugging into `src/data_manager.py` if needed.


