#!/bin/bash

# Check if running on Windows
if [[ "$(uname -s)" == *"MINGW"* ]] || [[ "$(uname -s)" == *"MSYS"* ]] || [[ "$(uname -s)" == *"CYGWIN"* ]]; then
  echo "🖥️ Detected Windows environment"
  # On Windows, make sure line endings are correct
  if command -v dos2unix &>/dev/null; then
    dos2unix dev
    echo "✅ Fixed line endings for dev script"
  else
    echo "⚠️ dos2unix not found. If you have issues, install it or manually convert line endings to LF."
  fi
else
  # Make the dev script executable
  chmod +x dev
fi

echo "✅ Setup complete! You can now run './dev up' to start the development environment."
echo ""
echo "If you're on Windows and have issues running './dev up', try these alternatives:"
echo "  - bash dev up"
echo "  - sh dev up" 