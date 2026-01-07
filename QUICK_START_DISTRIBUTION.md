# Quick Start: Sharing Your Package

## 🚀 Fastest Way: Git Repository

### Step 1: Push to GitHub/GitLab
```bash
git init
git add .
git commit -m "Initial release"
git remote add origin https://github.com/yourusername/ragforge.git
git push -u origin main
```

### Step 2: Share This Command with Users
```bash
pip install git+https://github.com/yourusername/ragforge.git
```

**That's it!** Users can now install your package.

---

## 📦 Alternative: Share Wheel File

### Step 1: Build the Package
```bash
uv build
# Creates: dist/ragforge-0.1.0-py3-none-any.whl
```

### Step 2: Share the .whl File
- Email it
- Upload to Google Drive/Dropbox
- Share via USB

### Step 3: Users Install It
```bash
pip install ragforge-0.1.0-py3-none-any.whl
```

---

## 🌐 For Public Release: PyPI

### Step 1: Create PyPI Account
- Go to https://pypi.org/account/register/

### Step 2: Build and Publish
```bash
uv build
uv publish
```

### Step 3: Users Install
```bash
pip install ragforge
```

---

## ✅ Test Your Distribution

Before sharing, test the installation:

```bash
# Test wheel file
pip install dist/ragforge-0.1.0-py3-none-any.whl
python -c "from ragforge import ask, ingest; print('✅ Success!')"

# Test from git (if published)
pip uninstall ragforge
pip install git+https://github.com/yourusername/ragforge.git
python -c "from ragforge import ask, ingest; print('✅ Success!')"
```

---

## 📋 What Users Need

Share these instructions with users:

1. **Install the package** (choose one method above)
2. **Set API key**:
   ```bash
   export GROQ_API_KEY="their_api_key"
   ```
3. **Use it**:
   ```python
   from ragforge import ask, ingest
   
   ingest(["Your knowledge here"])
   result = ask("Your question")
   print(result["answer"])
   ```

---

For detailed instructions, see [DISTRIBUTION.md](DISTRIBUTION.md)
