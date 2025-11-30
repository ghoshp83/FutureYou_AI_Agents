# 🚀 FutureYou Quick Start Guide

Get started with FutureYou in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- Gemini API key ([Get one here](https://ai.google.dev/))

## Installation

```bash
# Fork this repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/futureyou-ai-agents.git
cd futureyou-ai-agents

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

**Quick Test (Read-only):**
```bash
git clone https://github.com/pghosh5/futureyou-ai-agents.git
cd futureyou-ai-agents
```

## Quick Run

### Method 1: JSON Input (Recommended)

1. **Edit the input file:**
```bash
cp futureyou_input.json.example futureyou_input.json
# Edit futureyou_input.json with your information
```

2. **Run the simulation:**
```bash
python futureyou.py
```

### Method 2: Interactive Mode

```bash
python futureyou_interactive.py
```

Follow the prompts to enter your profile and decision.

## Example Input

```json
{
  "user_profile": {
    "user_id": "john_doe",
    "age": 28,
    "current_role": "Software Engineer",
    "skills": ["Python", "Machine Learning"],
    "life_goals": ["Financial independence", "Work-life balance"]
  },
  "decision": "Should I join a startup or stay at my current company?",
  "timelines": ["1yr", "3yr", "5yr"],
  "generate_visuals": true
}
```

## What You'll Get

- **Decision DNA** - Your unique decision-making profile
- **9 Future Scenarios** - 3 scenarios for each timeline (1yr, 3yr, 5yr)
- **Analysis** - Comparison of all scenarios
- **Personalized Advice** - Actionable recommendations with 30/60/90 day plans
- **Visualizations** - AI-generated diagrams (if enabled)

## Output Location

Results are saved to:
- `results/outputs/*.json` - Detailed results
- `results/visualizations/*.png` - Generated images

## Validation

Before running, validate your setup:
```bash
python config_validator.py
```

## Quick Troubleshooting

### "GEMINI_API_KEY not found"
Make sure you've created `.env` file with your API key:
```bash
GEMINI_API_KEY=your_api_key_here
```

### "Module not found"
Install dependencies:
```bash
pip install -r requirements.txt
```

### Slow execution
Normal execution time is 2-5 minutes per simulation. Each agent call takes 10-30 seconds.

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed problem solving

---

**Ready to simulate your future!** 🔮
