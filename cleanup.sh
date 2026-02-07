#!/bin/bash
# wArgs Documentation Cleanup Script
# This script automates the documentation and project cleanup tasks
set -e

echo "=== wArgs Documentation & Cleanup ==="
echo ""

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Create backup
echo "📦 Creating backup..."
BACKUP_FILE="../wArgs-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "$BACKUP_FILE" .
echo "✓ Backup created: $BACKUP_FILE"
echo ""

# Phase 1: Fix naming inconsistencies
echo "🔧 Phase 1: Fixing wargs → wArgs naming..."

# Replace "from wargs import" with "from wArgs import"
echo "  - Updating imports in docs/"
find docs -name "*.md" -type f -exec sed -i '' 's/from wargs import/from wArgs import/g' {} \; 2>/dev/null || true

echo "  - Updating imports in README.md and CONTRIBUTING.md"
sed -i '' 's/from wargs import/from wArgs import/g' README.md CONTRIBUTING.md 2>/dev/null || true

# Replace "@wargs" with "@wArgs"
echo "  - Updating decorator references in docs/"
find docs -name "*.md" -type f -exec sed -i '' 's/@wargs/@wArgs/g' {} \; 2>/dev/null || true

echo "  - Updating decorator references in README.md and CONTRIBUTING.md"
sed -i '' 's/@wargs/@wArgs/g' README.md CONTRIBUTING.md 2>/dev/null || true

# Fix mixed case imports
echo "  - Fixing mixed case imports"
find docs -name "*.md" -type f -exec sed -i '' 's/from wArgs import wargs/from wArgs import wArgs/g' {} \; 2>/dev/null || true
sed -i '' 's/from wArgs import wargs/from wArgs import wArgs/g' README.md CONTRIBUTING.md 2>/dev/null || true

echo "✓ Phase 1 complete"
echo ""

# Phase 2: Update URLs
echo "🔗 Phase 2: Updating URLs..."

# Replace placeholder username
echo "  - Replacing YOUR_USERNAME with cmoxiv"
sed -i '' 's|YOUR_USERNAME/wargs|cmoxiv/wArgs|g' README.md CONTRIBUTING.md 2>/dev/null || true

# Replace incorrect GitHub paths
echo "  - Updating GitHub repository paths"
sed -i '' 's|wargs/wargs|cmoxiv/wArgs|g' mkdocs.yml pyproject.toml 2>/dev/null || true

# Update documentation URL
echo "  - Setting documentation URL to GitHub Pages"
sed -i '' 's|https://wargs.readthedocs.io|https://cmoxiv.github.io/wArgs/|g' mkdocs.yml pyproject.toml 2>/dev/null || true

echo "✓ Phase 2 complete"
echo ""

# Phase 3: Cleanup files
echo "🧹 Phase 3: Cleaning up files..."

# Remove .DS_Store files
echo "  - Removing .DS_Store files"
DS_STORE_COUNT=$(find . -name ".DS_Store" -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$DS_STORE_COUNT" -gt 0 ]; then
    find . -name ".DS_Store" -type f -delete 2>/dev/null || true
    echo "  ✓ Removed $DS_STORE_COUNT .DS_Store files"
else
    echo "  ✓ No .DS_Store files found"
fi

# Update .gitignore
echo "  - Updating .gitignore"
if ! grep -q ".DS_Store" .gitignore 2>/dev/null; then
    cat >> .gitignore << 'EOF'

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Claude Code
.claude/
EOF
    echo "  ✓ Added macOS and Claude patterns to .gitignore"
else
    echo "  ✓ .gitignore already up to date"
fi

echo "✓ Phase 3 complete"
echo ""

# Verification
echo "=== Verification ==="
echo ""

# Count remaining issues
WARGS_IMPORT_COUNT=$(grep -r "from wargs import" docs/ *.md 2>/dev/null | wc -l | tr -d ' ')
WARGS_DECORATOR_COUNT=$(grep -r "@wargs" docs/ *.md 2>/dev/null | wc -l | tr -d ' ')
DS_STORE_REMAINING=$(find . -name ".DS_Store" 2>/dev/null | wc -l | tr -d ' ')
PLACEHOLDER_COUNT=$(grep -r "YOUR_USERNAME" *.md 2>/dev/null | wc -l | tr -d ' ')

echo "📊 Results:"
echo "  - Remaining 'from wargs import': $WARGS_IMPORT_COUNT"
echo "  - Remaining '@wargs': $WARGS_DECORATOR_COUNT"
echo "  - Remaining .DS_Store: $DS_STORE_REMAINING"
echo "  - Remaining YOUR_USERNAME: $PLACEHOLDER_COUNT"
echo ""

# Check for success
if [ "$WARGS_IMPORT_COUNT" -eq 0 ] && [ "$WARGS_DECORATOR_COUNT" -eq 0 ] && \
   [ "$DS_STORE_REMAINING" -eq 0 ] && [ "$PLACEHOLDER_COUNT" -eq 0 ]; then
    echo "✅ All cleanup tasks completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git status"
    echo "  2. Test documentation build: mkdocs build --strict"
    echo "  3. Commit changes: git add . && git commit -m 'docs: cleanup and standardize naming'"
else
    echo "⚠️  Some issues remain. Please review manually."
fi

echo ""
echo "=== Cleanup Complete ==="
