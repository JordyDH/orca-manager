#!/bin/bash

# Get the absolute directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="orca-manager"

# Determine shell config
if [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
else
    SHELL_CONFIG="$HOME/.bashrc"
fi

# 1. Remove *any* existing PATH block we may have added before
sed -i '/# ORCA_CLI_START/,/# ORCA_CLI_END/d' "$SHELL_CONFIG"
sed -i '/# ORCA_MANAGER_START/,/# ORCA_MANAGER_END/d' "$SHELL_CONFIG"

# 2. Add new clean block for orca-manager
{
    echo "# ORCA_MANAGER_START"
    echo "export PATH=\"\$PATH:$SCRIPT_DIR\""
    echo "# ORCA_MANAGER_END"
} >> "$SHELL_CONFIG"

# 3. Ensure the orca-manager script is executable
chmod +x "$SCRIPT_DIR/$SCRIPT_NAME"

# 4. Optional: create symlink if file is still named orca.py
if [ ! -f "$SCRIPT_DIR/$SCRIPT_NAME" ] && [ -f "$SCRIPT_DIR/orca.py" ]; then
    ln -sf "$SCRIPT_DIR/orca.py" "$SCRIPT_DIR/$SCRIPT_NAME"
    chmod +x "$SCRIPT_DIR/orca.py"
fi

echo "✅ orca-manager CLI installed from $SCRIPT_DIR"
echo "👉 Run: source $SHELL_CONFIG or restart your terminal"
