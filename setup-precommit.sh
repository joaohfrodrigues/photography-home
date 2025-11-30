#!/bin/bash
# Pre-commit setup script for photography-home project

set -e

echo "🔧 Setting up pre-commit hooks for photography-home..."
echo ""

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   Run: source .venv/bin/activate"
    echo ""
fi

# Install pre-commit
echo "📦 Installing pre-commit..."
pip install pre-commit

# Install other development dependencies
echo "📦 Installing development dependencies..."
pip install ruff bandit safety

# Install pre-commit hooks
echo "🪝 Installing git hooks..."
pre-commit install
pre-commit install --hook-type pre-push

# Run pre-commit on all files to ensure everything is set up correctly
echo "🧪 Running initial validation on all files..."
echo "   (This may take a minute on first run as it downloads tools)"
echo ""
pre-commit run --all-files || true

echo ""
echo "✅ Pre-commit setup complete!"
echo ""
echo "📋 Available commands:"
echo "   • Run hooks manually:          pre-commit run --all-files"
echo "   • Run hooks on staged files:   pre-commit run"
echo "   • Update hooks:                pre-commit autoupdate"
echo "   • Skip hooks (use sparingly):  git commit --no-verify"
echo ""
echo "💡 Hooks will now run automatically on git commit!"
