# Documentation Deployment Guide

Quick guide to deploy the updated documentation.

## Option 1: Deploy MkDocs to GitHub Pages (Recommended)

### One-Command Deployment
```bash
mkdocs gh-deploy
```

This will:
1. Build the documentation
2. Push to `gh-pages` branch
3. Make it live at https://cmoxiv.github.io/wArgs/

### Verify Deployment
- Visit: https://cmoxiv.github.io/wArgs/
- Check: https://cmoxiv.github.io/wArgs/tutorials/
- Test: Search functionality

## Option 2: Deploy Wiki to GitHub Wiki

### Method A: Git Push (Fastest)
```bash
cd wArgs.wiki

# Copy new wiki files if not already there
cp ../wArgs/wiki/*.md .

# Commit and push
git add *.md
git commit -m "Add tutorials and integration guides

- Add 4 complete tutorials (Database, File Manager, Web Scraper, System Monitor)
- Add Django and Flask integration guides
- Add community resources page
- Update home page with new navigation"

git push origin master
```

### Method B: Manual Copy/Paste
1. Go to https://github.com/cmoxiv/wArgs/wiki
2. For each file in `wiki/`:
   - Click "New Page"
   - Copy content from `.md` file
   - Paste and save

## Option 3: Deploy Both (Best)

```bash
# Deploy MkDocs to GitHub Pages
mkdocs gh-deploy

# Deploy Wiki
cd wArgs.wiki
git add *.md
git commit -m "Add comprehensive wiki content"
git push origin master
```

## Verification Checklist

After deployment, verify:

### MkDocs Site
- [ ] Home page loads: https://cmoxiv.github.io/wArgs/
- [ ] Tutorials section: https://cmoxiv.github.io/wArgs/tutorials/
- [ ] Integration guides: https://cmoxiv.github.io/wArgs/integrations/
- [ ] Search works
- [ ] Navigation works
- [ ] No broken links

### GitHub Wiki
- [ ] Home page loads: https://github.com/cmoxiv/wArgs/wiki
- [ ] Tutorial pages accessible
- [ ] Internal wiki links work
- [ ] Code blocks formatted correctly
- [ ] Images display (if any)

## Troubleshooting

### MkDocs gh-deploy fails
```bash
# Make sure you're on the right branch
git checkout main

# Ensure docs build locally first
mkdocs build --strict

# Try with verbose output
mkdocs gh-deploy --verbose
```

### Wiki push fails (authentication)
```bash
# Use SSH instead of HTTPS
git remote set-url origin git@github.com:cmoxiv/wArgs.wiki.git

# Or use GitHub CLI
gh auth login
```

### Broken links in MkDocs
```bash
# Check for warnings during build
mkdocs build --strict

# Fix any broken internal links
# Links should be relative: [Text](../page.md)
```

## Post-Deployment

### Announce Updates
1. Create GitHub Discussion post:
   ```markdown
   # 📚 Major Documentation Update!

   We've added comprehensive tutorials and guides to help you build CLIs with wArgs!

   **New Content:**
   - 4 complete tutorials (Database, File Manager, Web Scraper, System Monitor)
   - Django and Flask integration guides
   - Community resources page

   **Check it out:**
   - Documentation: https://cmoxiv.github.io/wArgs/tutorials/
   - Wiki: https://github.com/cmoxiv/wArgs/wiki

   Feedback welcome!
   ```

2. Update README.md (optional):
   ```markdown
   ## 📚 Documentation

   - **Tutorials**: [Step-by-step guides](https://cmoxiv.github.io/wArgs/tutorials/)
   - **Wiki**: [Community content](https://github.com/cmoxiv/wArgs/wiki)
   - **API Docs**: [Full reference](https://cmoxiv.github.io/wArgs/api/decorators/)
   ```

### Social Media (optional)
- Tweet about the update
- Post on relevant subreddits (r/Python, r/commandline)
- Share in Python Discord servers

## Continuous Updates

### Updating Content
```bash
# Edit docs or wiki
vim docs/tutorials/new-tutorial.md

# Build and test locally
mkdocs serve  # Preview at http://localhost:8000

# Deploy when ready
mkdocs gh-deploy
```

### Syncing Wiki Changes
```bash
# Pull latest wiki changes
cd wArgs.wiki
git pull

# Copy back to main repo
cp *.md ../wArgs/wiki/

# Commit in main repo
cd ../wArgs
git add wiki/
git commit -m "Sync wiki updates"
```

## Quick Commands Reference

```bash
# Build docs locally
mkdocs build

# Serve docs locally (live reload)
mkdocs serve

# Deploy to GitHub Pages
mkdocs gh-deploy

# Push wiki updates
cd wArgs.wiki && git push origin master

# Build with strict mode (fail on warnings)
mkdocs build --strict
```

---

**Ready to deploy? Run:** `mkdocs gh-deploy`
