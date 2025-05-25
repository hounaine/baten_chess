# Installation

## Prerequisites

- **Python 3.12** or newer  
- **pip** (bundled with Python)  
- **virtualenv** (optional but recommended)  
- **git**

## Setup

```bash
# Clone the repository
git clone https://github.com/hounaine/baten_chess.git
cd baten_chess

# Create and activate a virtual environment
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
Configuration
Set the Flask app environment variable:

# macOS / Linux
export FLASK_APP=app.py

# Windows (PowerShell)
powershell
$Env:FLASK_APP = "app.py"

# (Optional) enable development mode:
export FLASK_ENV=development

# Using Flask
flask run

# Or directly with Python
python app.py
The server will be available at:
http://127.0.0.1:5000

#Testing
pytest