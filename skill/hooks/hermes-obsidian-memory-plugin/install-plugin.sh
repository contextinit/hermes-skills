#!/bin/bash
# Hermes Obsidian Memory Plugin — Installer
# Usage: bash install-plugin.sh [--hermes-dir ~/.hermes]

set -euo pipefail

HERMES_DIR="${1:-$HOME/.hermes}"
PLUGIN_SRC="/vault/Hermes_Agent_Folder/Hermes_Memory/Hooks/hermes-obsidian-memory-plugin"
PLUGIN_DST="$HERMES_DIR/plugins/hermes-obsidian-memory"

echo "Installing Hermes Obsidian Memory Plugin..."
echo "  Source: $PLUGIN_SRC"
echo "  Target: $PLUGIN_DST"

# Create plugin directory
mkdir -p "$PLUGIN_DST"

# Copy plugin files
cp "$PLUGIN_SRC/__init__.py" "$PLUGIN_DST/__init__.py"

echo "✅ Plugin copied to $PLUGIN_DST"
echo ""
echo "Next steps:"
echo "  1. Restart Hermes (hermes restart or /reset)"
echo "  2. Verify plugin is loaded: hermes plugins list"
echo "  3. Check logs for 'hermes-obsidian-memory' startup messages"
echo ""
echo "If you use a non-default HERMES_HOME, pass it as an argument:"
echo "  bash install-plugin.sh /path/to/hermes_home"
