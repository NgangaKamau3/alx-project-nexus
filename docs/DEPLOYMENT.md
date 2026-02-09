# Deploying Documentation

Guide to deploying ModestWear API documentation.

## Deployment Options

### Option 1: Read the Docs (Recommended)

**Free, automatic builds, custom domain support**

1. **Sign up at [readthedocs.org](https://readthedocs.org)**

2. **Import Project:**
   - Click "Import a Project"
   - Connect GitHub account
   - Select `modestwear` repository

3. **Configure Build:**
   - Name: `modestwear-api`
   - Language: Python
   - Programming Language: Python 3.11
   - Requirements file: `docs/requirements.txt`
   - Documentation type: Sphinx

4. **Advanced Settings:**
   ```yaml
   # .readthedocs.yaml (create in project root)
   version: 2
   
   build:
     os: ubuntu-22.04
     tools:
       python: "3.11"
   
   sphinx:
     configuration: docs/conf.py
   
   python:
     install:
       - requirements: docs/requirements.txt
   ```

5. **Build & Deploy:**
   - Automatic builds on every push
   - URL: `https://modestwear-api.readthedocs.io`

### Option 2: GitHub Pages

**Free, simple, GitHub-integrated**

1. **Build Documentation:**
   ```bash
   cd docs
   pip install -r requirements.txt
   sphinx-build -b html source build/html
   ```

2. **Create gh-pages Branch:**
   ```bash
   # Install gh-pages tool
   npm install -g gh-pages
   
   # Deploy
   gh-pages -d docs/build/html
   ```

3. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: Deploy from branch
   - Branch: gh-pages
   - Folder: / (root)
   - Save

4. **Access Documentation:**
   - URL: `https://yourusername.github.io/modestwear/`

### Option 3: Vercel

**Free, fast, automatic deployments**

1. **Create vercel.json in docs folder:**
   ```json
   {
     "buildCommand": "pip install -r requirements.txt && sphinx-build -b html source build/html",
     "outputDirectory": "build/html",
     "installCommand": "pip install -r requirements.txt"
   }
   ```

2. **Deploy:**
   - Go to [vercel.com](https://vercel.com)
   - Import repository
   - Root directory: `docs`
   - Framework: Other
   - Build command: `pip install -r requirements.txt && sphinx-build -b html source build/html`
   - Output directory: `build/html`

3. **Access Documentation:**
   - URL: `https://modestwear-docs.vercel.app`

### Option 4: Netlify

**Free, simple, drag-and-drop**

1. **Build Locally:**
   ```bash
   cd docs
   pip install -r requirements.txt
   sphinx-build -b html source build/html
   ```

2. **Deploy:**
   - Go to [netlify.com](https://netlify.com)
   - Drag `docs/build/html` folder to deploy
   - Or connect GitHub for automatic builds

3. **Build Settings (for automatic):**
   - Base directory: `docs`
   - Build command: `pip install -r requirements.txt && sphinx-build -b html source build/html`
   - Publish directory: `docs/build/html`

## Recommended Setup

**For ModestWear:**

1. **API Backend:** Render
   - URL: `https://modestwear.onrender.com`
   - Swagger: `https://modestwear.onrender.com/docs/`

2. **Frontend:** Vercel
   - URL: `https://modestwear-app.vercel.app`

3. **Documentation:** Read the Docs
   - URL: `https://modestwear-api.readthedocs.io`
   - Or: `https://docs.modestwear.com` (custom domain)

## Custom Domain

### Read the Docs

1. **Add Domain:**
   - Project Settings → Domains
   - Add `docs.modestwear.com`

2. **DNS Configuration:**
   ```
   Type: CNAME
   Name: docs
   Value: modestwear-api.readthedocs.io
   ```

### GitHub Pages

1. **Add CNAME file:**
   ```bash
   echo "docs.modestwear.com" > docs/build/html/CNAME
   ```

2. **DNS Configuration:**
   ```
   Type: CNAME
   Name: docs
   Value: yourusername.github.io
   ```

## Automatic Updates

All options support automatic builds on git push:

```bash
git add docs/
git commit -m "Update documentation"
git push origin main
# Documentation automatically rebuilds
```

## Local Preview

Before deploying, always preview locally:

```bash
cd docs
pip install -r requirements.txt
sphinx-build -b html source build/html
python -m http.server 8000 --directory build/html
# Open http://localhost:8000
```

## URLs Summary

| Service | URL | Purpose |
|---------|-----|---------|
| API Backend | https://modestwear.onrender.com | REST API |
| Swagger UI | https://modestwear.onrender.com/docs/ | Interactive API testing |
| ReDoc | https://modestwear.onrender.com/redoc/ | API reference |
| Frontend | https://modestwear-app.vercel.app | Web application |
| Documentation | https://modestwear-api.readthedocs.io | Full documentation |

## Next Steps

1. Choose deployment option (Read the Docs recommended)
2. Deploy documentation
3. Update README with documentation URL
4. Share with mentors/reviewers
