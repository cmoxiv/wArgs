# wArgs Community Wiki

Welcome to the wArgs community wiki! This is a collaborative space for tutorials, guides, and community-contributed resources.

## 📚 Official Documentation

For official documentation, please visit:
- **Documentation Site**: [https://cmoxiv.github.io/wArgs/](https://cmoxiv.github.io/wArgs/)
- **GitHub Repository**: [https://github.com/cmoxiv/wArgs](https://github.com/cmoxiv/wArgs)
- **ROADMAP**: [Feature Roadmap](https://github.com/cmoxiv/wArgs/blob/main/ROADMAP.md)

## 🎯 What's in the Wiki?

This wiki contains **community-contributed content** including:

### 📖 Tutorials
Step-by-step guides for building real-world CLIs:
- [[Building a Database CLI]] - Create a PostgreSQL/MySQL admin tool
- [[Building a File Manager CLI]] - File operations and navigation
- [[Building a Web Scraper CLI]] - Scraping websites with wArgs
- [[Building a System Monitor CLI]] - Monitor system resources
- [[Building a Git Helper CLI]] - Custom git workflow tools

### 🔧 Integration Guides
Using wArgs with popular frameworks:
- [[Django Management Commands]] - Integrate with Django
- [[Flask CLI Integration]] - Build Flask CLI tools
- [[FastAPI CLI Tools]] - Create FastAPI companion CLIs
- [[SQLAlchemy Schema Tools]] - Database schema management

### 💡 Use Case Studies
Real-world examples and case studies:
- [[Case Study: Data Processing Pipeline]] - ETL pipeline CLI
- [[Case Study: DevOps Automation]] - Deployment automation
- [[Case Study: Testing Framework]] - Custom test runner

### 🌟 Community Resources
- [[Community Plugins]] - Third-party plugins and extensions
- [[Blog Posts and Articles]] - Community writings
- [[Video Tutorials]] - YouTube tutorials and screencasts
- [[Related Projects]] - Projects using wArgs

## 🤝 Contributing to the Wiki

Want to add your own tutorial or guide? Great!

1. **Read the guidelines**: [[Contributing to Wiki]]
2. **Use the templates**: Start with a template for consistency
3. **Share your work**: Create a new page and add it to the navigation

## 💬 Getting Help

- **Questions**: [GitHub Discussions](https://github.com/cmoxiv/wArgs/discussions)
- **Bugs**: [GitHub Issues](https://github.com/cmoxiv/wArgs/issues)
- **FAQ**: [Official FAQ](https://cmoxiv.github.io/wArgs/faq/)
- **Troubleshooting**: [Troubleshooting Guide](https://cmoxiv.github.io/wArgs/troubleshooting/)

## 🌟 Quick Start

New to wArgs? Start here:

```python
from wArgs import wArgs

@wArgs
def hello(name: str, greeting: str = "Hello"):
    """Greet someone."""
    print(f"{greeting}, {name}!")

if __name__ == "__main__":
    hello()
```

```bash
python hello.py --hello-name World --hello-greeting Hi
# Output: Hi, World!
```

## 📝 Wiki Index

**Tutorials:**
- Building a Database CLI
- Building a File Manager CLI
- Building a Web Scraper CLI
- Building a System Monitor CLI
- Building a Git Helper CLI

**Integration Guides:**
- Django Management Commands
- Flask CLI Integration
- FastAPI CLI Tools
- SQLAlchemy Schema Tools

**Resources:**
- Contributing to Wiki
- Community Plugins
- Blog Posts and Articles
- Video Tutorials

---

*This wiki is maintained by the wArgs community. Pages may contain unofficial content. For official documentation, see the [docs site](https://cmoxiv.github.io/wArgs/).*
