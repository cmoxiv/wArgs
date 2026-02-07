# Quick Wiki Setup Guide

Follow these steps to populate your GitHub Wiki with the prepared content.

## Prerequisites

- GitHub repository with Wiki enabled
- Wiki should be accessible at: https://github.com/cmoxiv/wArgs/wiki

## Option 1: Manual Copy/Paste (Recommended for First Time)

### Step 1: Create Home Page

1. Go to https://github.com/cmoxiv/wArgs/wiki
2. Click **"Create the first page"** or **"New Page"**
3. Name the page: **Home**
4. Open `wiki/Home.md` in this directory
5. Copy **all content** from `Home.md`
6. Paste into the GitHub Wiki editor
7. Click **"Save Page"**

### Step 2: Add Contribution Guide

1. Click **"New Page"** in the wiki
2. Name: **Contributing to Wiki**
3. Copy content from `wiki/Contributing-to-Wiki.md`
4. Paste and save

### Step 3: Add First Tutorial

1. Click **"New Page"**
2. Name: **Building a Database CLI**
3. Copy content from `wiki/Building-a-Database-CLI.md`
4. Paste and save

### Step 4: Add More Pages

Repeat for each file:
- `Building-a-File-Manager-CLI.md` → **Building a File Manager CLI**
- `Django-Management-Commands.md` → **Django Management Commands**

**Important**: 
- Remove the `.md` extension when creating the page name in GitHub
- GitHub will auto-convert "Building a Database CLI" to "Building-a-Database-CLI" in URLs

## Option 2: Clone and Push (Advanced)

### Step 1: Clone Wiki Repository

```bash
# Clone the wiki (it's a separate Git repo)
git clone https://github.com/cmoxiv/wArgs.wiki.git

# Navigate to wiki repo
cd wArgs.wiki
```

### Step 2: Copy Files

```bash
# Copy all wiki content
cp ../wArgs/wiki/*.md .

# Remove the setup files
rm README.md SETUP-GUIDE.md
```

### Step 3: Push to Wiki

```bash
# Add all files
git add *.md

# Commit
git commit -m "Initial wiki content

- Add Home page with navigation
- Add Database CLI tutorial
- Add File Manager CLI tutorial
- Add Django integration guide
- Add contribution guidelines"

# Push to wiki
git push origin master
```

## Verification

After publishing, verify:

1. **Home page loads**: https://github.com/cmoxiv/wArgs/wiki
2. **Navigation works**: Click links to other pages
3. **Formatting looks good**: Check code blocks and headings
4. **Links work**: Internal wiki links and external links

## Troubleshooting

### "Page not found" when clicking wiki links

- Check page names match exactly (case-sensitive)
- Internal links use format: `[[Page Name]]`
- Page name in GitHub should match what's in the link

### Code blocks not formatted

- Ensure you used triple backticks: ```
- Specify language: ```python or ```bash
- Check for proper closing ```

### Images not showing

- GitHub wiki doesn't support relative image paths in wikis
- Use absolute URLs or upload images to GitHub Issues and reference them

## Customization

After publishing, you can:

- **Edit pages** directly in GitHub Wiki editor
- **Add new pages** using the "New Page" button
- **Reorganize** by editing the Home page navigation
- **Add images** by uploading to wiki or issues

## Keeping Wiki Updated

Two-way sync between local files and GitHub Wiki:

### Local → GitHub Wiki
```bash
# Make changes locally
vim wiki/Home.md

# Copy to wiki repo
cp wiki/*.md ../wArgs.wiki/

# Commit and push
cd ../wArgs.wiki
git add .
git commit -m "Update wiki content"
git push
```

### GitHub Wiki → Local
```bash
# Pull latest changes from wiki
cd wArgs.wiki
git pull

# Copy back to main repo
cp *.md ../wArgs/wiki/
```

## Next Steps

1. ✅ Publish initial wiki pages
2. 📝 Create additional tutorials (use templates in Contributing-to-Wiki.md)
3. 🔗 Link to wiki from main README.md
4. 📢 Announce wiki in GitHub Discussions
5. 🤝 Invite community contributions

## Wiki Announcement Template

Post this in GitHub Discussions after setup:

```markdown
# 📚 New Community Wiki!

We've created a community wiki with tutorials and guides for wArgs!

**What's in the wiki:**
- Building a Database CLI - Complete tutorial
- Building a File Manager CLI - Step-by-step guide
- Django Management Commands - Integration guide
- And more coming soon!

**Check it out:** https://github.com/cmoxiv/wArgs/wiki

**Contribute:** See the [Contributing to Wiki](https://github.com/cmoxiv/wArgs/wiki/Contributing-to-Wiki) guide to add your own tutorials!
```

## Questions?

If you have issues setting up the wiki:
1. Check GitHub's [Wiki documentation](https://docs.github.com/en/communities/documenting-your-project-with-wikis)
2. Open an issue in the main repo
3. Ask in GitHub Discussions

---

**Happy wiki building! 🎉**
