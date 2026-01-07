# Distribution Guide for Ragforge

This guide provides step-by-step instructions for sharing the Ragforge package with others.

## Prerequisites

- Python 3.9+ installed
- Package is tested and working
- `pyproject.toml` is properly configured

## Method 1: Git Repository (Recommended)

### For Package Maintainer

1. **Initialize Git Repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial release"
   ```

2. **Create .gitignore** (if not exists):
   ```bash
   cat > .gitignore << EOF
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   .Python
   build/
   develop-eggs/
   dist/
   downloads/
   eggs/
   .eggs/
   lib/
   lib64/
   parts/
   sdist/
   var/
   wheels/
   *.egg-info/
   .installed.cfg
   *.egg
   .venv/
   venv/
   ENV/
   env/
   .env
   *.sqlite
   qdrant_data/
   .fastembed_cache/
   EOF
   ```

3. **Push to Remote Repository**:
   ```bash
   git remote add origin https://github.com/yourusername/ragforge.git
   git branch -M main
   git push -u origin main
   ```

4. **Create a Release Tag**:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

### For Users

```bash
# Install from GitHub
pip install git+https://github.com/yourusername/ragforge.git

# Install specific version/tag
pip install git+https://github.com/yourusername/ragforge.git@v0.1.0

# Install from private repository (requires authentication)
pip install git+https://github.com/yourusername/ragforge.git
# Or use SSH:
pip install git+ssh://git@github.com/yourusername/ragforge.git
```

## Method 2: Build Wheel File

### For Package Maintainer

1. **Install Build Tools**:
   ```bash
   pip install build
   # OR
   pip install uv
   ```

2. **Build the Package**:
   ```bash
   # Using build
   python -m build

   # OR using uv (faster)
   uv build
   ```

3. **Check Output**:
   ```bash
   ls dist/
   # Should see:
   # - ragforge-0.1.0-py3-none-any.whl
   # - ragforge-0.1.0.tar.gz
   ```

4. **Share the .whl File**:
   - Email it
   - Upload to file sharing service
   - Host on internal server
   - Share via USB drive

### For Users

```bash
# Download the .whl file first, then:
pip install ragforge-0.1.0-py3-none-any.whl

# Or from URL:
pip install https://example.com/path/to/ragforge-0.1.0-py3-none-any.whl
```

## Method 3: Publish to PyPI

### For Package Maintainer

1. **Create PyPI Account**:
   - Go to https://pypi.org/account/register/
   - Verify your email
   - (Optional) Create API token at https://pypi.org/manage/account/token/

2. **Update pyproject.toml**:
   ```toml
   [project]
   name = "ragforge"  # Must be unique!
   version = "0.1.0"
   description = "A zero-configuration, opinionated RAG pipeline."
   authors = [
       {name = "Your Name", email = "your.email@example.com"}
   ]
   license = {text = "MIT"}
   keywords = ["rag", "llm", "vector-database", "qdrant"]
   ```

3. **Build the Package**:
   ```bash
   uv build
   ```

4. **Test on TestPyPI First** (recommended):
   ```bash
   # Create account at https://test.pypi.org
   uv publish --publish-url https://test.pypi.org/legacy/
   
   # Test installation
   pip install --index-url https://test.pypi.org/simple/ ragforge
   ```

5. **Publish to PyPI**:
   ```bash
   # Using uv
   uv publish
   
   # OR using twine
   pip install twine
   twine upload dist/*
   ```

### For Users

```bash
# Simple installation
pip install ragforge

# Install specific version
pip install ragforge==0.1.0

# Upgrade to latest
pip install --upgrade ragforge
```

## Method 4: Local Development Installation

For users who want to contribute or test:

```bash
# Clone the repository
git clone https://github.com/yourusername/ragforge.git
cd ragforge

# Install in development mode (editable)
pip install -e .

# OR with development dependencies
pip install -e ".[dev]"
```

## Updating the Package

### For New Versions

1. **Update Version** in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # Increment version
   ```

2. **Update CHANGELOG.md** (if you have one)

3. **Commit and Tag**:
   ```bash
   git add .
   git commit -m "Release v0.1.1"
   git tag -a v0.1.1 -m "Release version 0.1.1"
   git push origin main --tags
   ```

4. **Rebuild and Republish**:
   ```bash
   uv build
   uv publish  # If using PyPI
   ```

## Troubleshooting

### Common Issues

1. **"Package not found" error**:
   - Check package name spelling
   - Verify the repository URL is correct
   - Ensure the package is published/accessible

2. **"No module named 'ragforge'"**:
   - Verify installation: `pip list | grep ragforge`
   - Check Python environment: `which python`
   - Reinstall: `pip install --force-reinstall ragforge`

3. **Build errors**:
   - Ensure all dependencies are in `pyproject.toml`
   - Check Python version compatibility
   - Verify `__init__.py` files exist

4. **Import errors after installation**:
   - Check package structure matches `pyproject.toml`
   - Verify `[tool.setuptools.packages.find]` configuration

## Best Practices

1. **Always test before sharing**:
   ```bash
   # Test installation in clean environment
   python -m venv test_env
   source test_env/bin/activate
   pip install your-package
   python -c "from ragforge import ask, ingest; print('Success!')"
   ```

2. **Use semantic versioning**:
   - MAJOR.MINOR.PATCH (e.g., 1.2.3)
   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes

3. **Document dependencies**:
   - List all required packages in `pyproject.toml`
   - Specify version constraints when needed

4. **Include examples**:
   - Add example scripts
   - Update README with usage examples

5. **Tag releases**:
   - Use git tags for version tracking
   - Create GitHub/GitLab releases with notes

## Quick Reference

| Task | Command |
|------|---------|
| Build package | `uv build` or `python -m build` |
| Install from git | `pip install git+https://github.com/user/repo.git` |
| Install from wheel | `pip install package.whl` |
| Install from PyPI | `pip install ragforge` |
| Publish to PyPI | `uv publish` or `twine upload dist/*` |
| Check installed version | `pip show ragforge` |
| Uninstall | `pip uninstall ragforge` |
