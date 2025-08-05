#!/bin/bash
# Fix Claude CLI in WSL
echo "Installing Claude CLI in WSL..."

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "npm not found. Installing Node.js and npm..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install Claude CLI globally in WSL
npm install -g @anthropic-ai/claude-code

echo "Claude CLI installation complete!"
echo "You can now run 'claude' directly in WSL"
