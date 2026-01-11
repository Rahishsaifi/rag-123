# Installation Fix for tiktoken

If you encounter the tiktoken installation error (Rust compiler required), here are solutions:

## Option 1: Upgrade pip and retry (Recommended)

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Option 2: Install Rust (if Option 1 doesn't work)

If prebuilt wheels aren't available for your Python version:

```bash
# Install Rust using rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Then retry installation
pip install -r requirements.txt
```

## Option 3: Use Python 3.11 or 3.12 (Alternative)

tiktoken has better wheel support for Python 3.11 and 3.12:

```bash
# Create venv with Python 3.11 or 3.12
python3.11 -m venv venv
# or
python3.12 -m venv venv

source venv/bin/activate
pip install -r requirements.txt
```

## Note

The chunking service has a fallback mechanism - if tiktoken is not available, it will use character-based chunking instead. The application will still work, but token counting will be approximate.

