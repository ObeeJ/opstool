#!/bin/bash

# Navigate to project directory
cd /c/Users/OBANIJESU/Documents/GoProjects/opstool/scripts

# Deactivate and remove existing virtual environment
deactivate 2>/dev/null
rm -rf venv

# Reinstall Python 3.12 via Chocolatey (assumes Chocolatey is installed)
choco install python3 --version=3.12.0 -y

# Verify Python 3.12 path
PYTHON312="/c/ProgramData/chocolatey/bin/python.exe"
if [ ! -f "$PYTHON312" ]; then
    echo "Python 3.12 not found at $PYTHON312. Please install manually from https://www.python.org/downloads/release/python-3120/"
    exit 1
fi

# Create new virtual environment with Python 3.12
"$PYTHON312" -m venv venv
source venv/Scripts/activate

# Verify Python version
if ! python --version | grep -q "3.12.0"; then
    echo "Virtual environment is not using Python 3.12.0. Exiting."
    exit 1
fi

# Upgrade pip
python -m pip install --upgrade pip

# Download and install precompiled wheels
curl -L -o psycopg2_binary-2.9.9-cp312-cp312-win_amd64.whl https://files.pythonhosted.org/packages/a7/81/20a4f351e25f3b9fb9f6d7736d3a0550755f06e4dd2eb0172cd9f5cf76ec/psycopg2_binary-2.9.9-cp312-cp312-win_amd64.whl
curl -L -o aiohttp-3.9.1-cp312-cp312-win_amd64.whl https://files.pythonhosted.org/packages/3a/30/a6d3e8d965fb4f8ed25a7d5d8a2a9d80a0576d6b7dc4f15ae5d39032a8ca/aiohttp-3.9.1-cp312-cp312-win_amd64.whl
pip install psycopg2_binary-2.9.9-cp312-cp312-win_amd64.whl
pip install aiohttp-3.9.1-cp312-cp312-win_amd64.whl

# Modify requirements.txt to comment out psycopg2-binary and aiohttp
sed -i 's/psycopg2-binary==2.9.9/# psycopg2-binary==2.9.9/' requirements.txt
sed -i 's/aiohttp==3.9.1/# aiohttp==3.9.1/' requirements.txt

# Install remaining requirements
pip install -r requirements.txt

# Set PostgreSQL environment variables
export LIB="C:\\Program Files\\PostgreSQL\\17\\lib;$LIB"
export INCLUDE="C:\\Program Files\\PostgreSQL\\17\\include;$INCLUDE"

# Optionally remove Python 3.13
rm -rf /c/Users/OBANIJESU/AppData/Local/Programs/Python/Python313

# Verify Python installations
echo "Python installations found:"
where python

echo "Setup complete. Virtual environment is ready with Python 3.12.0."
