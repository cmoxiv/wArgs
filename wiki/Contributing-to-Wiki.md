# Contributing to the Wiki

Thank you for your interest in contributing to the wArgs wiki! This guide will help you create high-quality tutorials and guides.

## What to Contribute

We welcome:
- ✅ **Tutorials** - Step-by-step guides for building CLIs
- ✅ **Integration guides** - Using wArgs with frameworks/libraries
- ✅ **Use case studies** - Real-world examples from your projects
- ✅ **Tips and tricks** - Best practices and patterns
- ✅ **Video tutorials** - Links to YouTube/screencasts
- ✅ **Blog posts** - Links to your articles about wArgs

We ask that you **don't**:
- ❌ Duplicate official documentation (link to it instead)
- ❌ Promote unrelated products/services
- ❌ Post incomplete or untested code

## Getting Started

1. **Check existing pages** - Avoid duplicates
2. **Use a template** - See templates below
3. **Test your code** - All examples should work
4. **Follow style guide** - Keep consistent formatting

## Page Templates

### Tutorial Template

```markdown
# Building a [Project Type] CLI

Brief description of what we'll build.

## Overview

Build a CLI that can:
- Feature 1
- Feature 2
- Feature 3

**Prerequisites:**
- Python 3.8+
- List dependencies
- Required knowledge

## Step 1: Project Setup

\`\`\`bash
# Setup commands
\`\`\`

## Step 2: Basic Structure

\`\`\`python
# Code example with comments
\`\`\`

## Step 3: [Feature Name]

Explanation of what we're building.

\`\`\`python
# Implementation
\`\`\`

## Usage Examples

\`\`\`bash
# How to use it
\`\`\`

## Advanced Features

Optional enhancements.

## Complete Example

Link to full code or GitHub repo.

## Related

- Links to related wiki pages
- Links to official docs
```

### Integration Guide Template

```markdown
# [Framework] Integration with wArgs

How to use wArgs with [Framework Name].

## Why wArgs for [Framework]?

- Benefit 1
- Benefit 2
- Benefit 3

## Basic Integration

### Step 1: Setup

\`\`\`python
# Setup code
\`\`\`

### Step 2: Create Command

\`\`\`python
# Example command
\`\`\`

## Real-World Examples

### Example 1: [Use Case]

\`\`\`python
# Code
\`\`\`

### Example 2: [Use Case]

\`\`\`python
# Code
\`\`\`

## Best Practices

1. Practice 1
2. Practice 2

## Testing

How to test commands.

## Complete Example

Link to full example.

## Related

- Related pages
```

### Use Case Study Template

```markdown
# Case Study: [Project Name]

Real-world example of using wArgs in production.

## Project Overview

- **Project**: Project name
- **Industry**: Industry/domain
- **Problem**: What problem it solved
- **Stack**: Technologies used

## The Challenge

Describe the problem you faced.

## The Solution

How you used wArgs to solve it.

\`\`\`python
# Key code examples
\`\`\`

## Implementation

Technical details.

## Results

- Metric 1
- Metric 2
- Lessons learned

## Code

Link to code (if public).

## Conclusion

Summary and takeaways.
```

## Style Guide

### Code Examples

**DO:**
```python
from wArgs import wArgs

@wArgs
def greet(name: str, count: int = 1):
    """Greet someone.

    Args:
        name: Person to greet
        count: Number of greetings
    """
    for _ in range(count):
        print(f"Hello, {name}!")
```

**DON'T:**
```python
# Incomplete example
def greet(name):
    print(f"Hello, {name}!")  # Missing decorator, types, docstring
```

### Formatting

- Use **Markdown headings** properly (H1 for title, H2 for sections)
- Include **code comments** for complex logic
- Use **syntax highlighting** (specify language: ```python, ```bash)
- Add **emojis** sparingly for visual markers (✅, ❌, 📚, etc.)
- Keep **line length** reasonable (wrap at ~80-100 chars)

### Writing Style

- Use **active voice** - "Create a function" not "A function is created"
- Be **concise** - Get to the point quickly
- Use **examples** - Show, don't just tell
- **Test everything** - All code must be tested and working
- **Link generously** - Reference official docs and related pages

## Linking to Other Pages

### Internal Wiki Links
```markdown
See [[Building a Database CLI]] for database examples.
```

### External Links
```markdown
Read the [official docs](https://cmoxiv.github.io/wArgs/) for more info.
See [GitHub repo](https://github.com/cmoxiv/wArgs) for examples.
```

## How to Create a New Page

1. **Click "New Page"** in GitHub Wiki
2. **Choose a descriptive name** - Use hyphens for spaces
   - Good: `Building-a-Database-CLI`
   - Bad: `db_cli` or `database`
3. **Use a template** from above
4. **Write your content**
5. **Preview** before saving
6. **Add to navigation** - Update the Home page with a link

## Page Naming Conventions

- Use **title case** with hyphens: `Building-a-File-Manager`
- Be **specific**: `Django-Management-Commands` not `Django`
- Avoid **special characters**: No spaces, underscores, or symbols
- Keep it **concise**: Aim for 2-5 words

## Examples of Good Pages

- [[Building a Database CLI]] - Comprehensive tutorial
- [[Django Management Commands]] - Framework integration
- [[Building a File Manager CLI]] - Practical example

## Quality Checklist

Before publishing, verify:

- [ ] Code examples are complete and tested
- [ ] All dependencies are listed
- [ ] Usage examples are included
- [ ] Links work (no broken links)
- [ ] Formatting is consistent
- [ ] Spelling and grammar checked
- [ ] Added to Home page navigation
- [ ] Used appropriate template

## Getting Help

Need help creating a page?

- **Questions**: [GitHub Discussions](https://github.com/cmoxiv/wArgs/discussions)
- **Feedback**: Ask in discussions before publishing
- **Examples**: Look at existing wiki pages for inspiration

## Recognition

Contributors who create quality wiki pages will be:
- Listed in the wiki contributors section
- Credited in their page (optional)
- Recognized in community updates

## Updates and Maintenance

- **Keep pages current** - Update when wArgs changes
- **Fix broken links** - Report or fix outdated links
- **Improve existing pages** - All pages can be edited
- **Archive outdated content** - Mark deprecated information

## Questions?

- Open a [Discussion](https://github.com/cmoxiv/wArgs/discussions)
- Tag your post with `wiki`
- Ask for help from maintainers

---

**Thank you for contributing to the wArgs community! 🎉**
