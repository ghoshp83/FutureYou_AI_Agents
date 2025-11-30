# 🔧 FutureYou Troubleshooting Guide

This guide helps you resolve common issues when setting up and running FutureYou.

---

## 🚀 Quick Setup Validation

Before troubleshooting, run the system validator:

```bash
python config_validator.py
```

This will check your environment, dependencies, and input file automatically.

---

## 📋 Common Issues & Solutions

### 1. API Key Issues

#### ❌ Error: "GEMINI_API_KEY not found in environment variables"

**Solution:**
```bash
# 1. Copy the example environment file
cp .env.example .env

# 2. Edit .env and add your API key
# Replace 'your_gemini_api_key_here' with your actual key
GEMINI_API_KEY=your_actual_api_key_here
```

**Get API Key:**
1. Go to [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

#### ❌ Error: "Failed to configure Gemini API"

**Possible causes:**
- Invalid API key format
- Network connectivity issues
- API key doesn't have proper permissions

**Solutions:**
1. Verify your API key is correct
2. Check internet connection
3. Try regenerating the API key

### 2. Installation Issues

#### ❌ Error: "ModuleNotFoundError: No module named 'google.generativeai'"

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install google-generativeai>=0.3.0
pip install tenacity>=8.0.0
pip install python-dotenv>=1.0.0
pip install Pillow>=10.0.0
```

#### ❌ Error: "pip install fails with permission error"

**Solution (macOS/Linux):**
```bash
# Use virtual environment (recommended)
python -m venv futureyou_env
source futureyou_env/bin/activate
pip install -r requirements.txt

# Or use user install
pip install --user -r requirements.txt
```

**Solution (Windows):**
```cmd
# Use virtual environment (recommended)
python -m venv futureyou_env
futureyou_env\Scripts\activate
pip install -r requirements.txt

# Or use user install
pip install --user -r requirements.txt
```

### 3. Input File Issues

#### ❌ Error: "futureyou_input.json not found"

**Solution:**
```bash
# Copy the example file
cp futureyou_input.json.example futureyou_input.json

# Edit with your information
nano futureyou_input.json  # or use your preferred editor
```

#### ❌ Error: "Invalid JSON in futureyou_input.json"

**Common JSON errors:**
- Missing commas between items
- Extra commas at end of lists
- Unmatched quotes or brackets
- Comments (not allowed in JSON)

**Solution:**
1. Use a JSON validator: [jsonlint.com](https://jsonlint.com/)
2. Check the example file format
3. Ensure proper escaping of quotes in strings

**Valid JSON example:**
```json
{
  "user_profile": {
    "user_id": "john_doe",
    "age": 28,
    "current_role": "Software Engineer"
  },
  "decision": "Should I start my own company?",
  "timelines": ["1yr", "3yr", "5yr"],
  "generate_visuals": true
}
```

### 4. Runtime Issues

#### ❌ Error: "Empty response from Gemini API"

**Possible causes:**
- API rate limiting
- Network timeout
- Invalid prompt format

**Solutions:**
1. Wait a few minutes and try again
2. Check internet connection
3. Verify API key has sufficient quota

#### ❌ Error: "Failed to parse JSON from Gemini response"

**Cause:** AI model returned malformed JSON

**Solutions:**
1. Try running again (AI responses can vary)
2. Simplify your decision text
3. Check if your input contains special characters

#### ❌ Error: "Permission denied creating results directory"

**Solution:**
```bash
# Create directories manually
mkdir -p results/outputs
mkdir -p results/visualizations

# Or run with appropriate permissions
sudo python futureyou.py  # Not recommended
```

### 5. Performance Issues

#### ⚠️ Slow response times

**Causes:**
- Large input data
- Network latency
- API rate limiting

**Solutions:**
1. Reduce input complexity
2. Check internet speed
3. Try during off-peak hours

#### ⚠️ High memory usage

**Solutions:**
1. Close other applications
2. Reduce number of timelines
3. Set `generate_visuals: false`

### 6. Visualization Issues

#### ❌ Error: "Visualization failed"

**Possible causes:**
- Missing Pillow dependency
- Insufficient disk space
- Permission issues

**Solutions:**
```bash
# Reinstall Pillow
pip uninstall Pillow
pip install Pillow>=10.0.0

# Check disk space
df -h  # Linux/macOS
dir   # Windows

# Set generate_visuals to false as workaround
```

---

## 🔍 Debugging Steps

### 1. Enable Verbose Logging

Check the `futureyou.log` file for detailed error information:

```bash
tail -f futureyou.log
```

### 2. Test Individual Components

```bash
# Test configuration
python config_validator.py

# Test with minimal input
python -c "
import json
data = {
    'user_profile': {'user_id': 'test', 'age': 25, 'current_role': 'Test'},
    'decision': 'Should I test this system?',
    'timelines': ['1yr'],
    'generate_visuals': false
}
with open('test_input.json', 'w') as f:
    json.dump(data, f)
"

# Run with test input
python futureyou.py
```

### 3. Check System Requirements

**Minimum Requirements:**
- Python 3.10+
- 4GB RAM
- 1GB free disk space
- Internet connection
- Valid Gemini API key

**Check Python version:**
```bash
python --version
# Should show 3.10 or higher
```

---

## 🆘 Getting Help

### 1. Check Logs

Always check `futureyou.log` for detailed error messages:

```bash
# View recent logs
tail -20 futureyou.log

# Search for errors
grep -i error futureyou.log
```

### 2. Run Validation

```bash
python config_validator.py
```

### 3. Test with Minimal Input

Create a simple test case:

```json
{
  "user_profile": {
    "user_id": "test_user",
    "age": 25,
    "current_role": "Tester"
  },
  "decision": "Should I test this system with minimal input?",
  "timelines": ["1yr"],
  "generate_visuals": false
}
```

### 4. Environment Information

When reporting issues, include:

```bash
# System info
python --version
pip list | grep -E "(google|tenacity|dotenv|Pillow)"

# File permissions
ls -la futureyou_input.json
ls -la .env

# Directory structure
ls -la results/
```

---

## 📞 Support Resources

1. **Configuration Validator**: `python config_validator.py`
2. **Unit Tests**: `python test_futureyou.py`
3. **Log Files**: Check `futureyou.log`
4. **Example Files**: Use `.example` files as templates
5. **Documentation**: See `README.md` and `QUICKSTART.md`

---

## 🔄 Reset to Clean State

If all else fails, reset to a clean state:

```bash
# 1. Remove generated files
rm -rf results/
rm futureyou.log
rm futureyou_input.json

# 2. Recreate from examples
cp futureyou_input.json.example futureyou_input.json
cp .env.example .env

# 3. Reinstall dependencies
pip uninstall -y google-generativeai tenacity python-dotenv Pillow
pip install -r requirements.txt

# 4. Validate setup
python config_validator.py

# 5. Test run
python futureyou.py
```

---

**Remember:** Most issues are related to API key setup or input file format. Always run `python config_validator.py` first!