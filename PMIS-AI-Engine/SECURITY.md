# 🔒 Security Guide - PMIS-AI Smart Allocation Engine

## 🚨 **CRITICAL: Secrets & Environment Variables**

### ⚠️ **NEVER COMMIT THESE TO GIT:**

1. **`.env` file** - Contains all sensitive configuration
2. **Private keys** - Blockchain wallet private keys
3. **API tokens** - Hugging Face, OpenAI, cloud provider keys
4. **Database credentials** - Passwords, connection strings
5. **Admin passwords** - System administration credentials

### 🔐 **Secrets Management Checklist**

#### **Before Git Commit:**
- [ ] ✅ `.env` is in `.gitignore`
- [ ] ✅ No hardcoded passwords in source code
- [ ] ✅ No API keys in Python files
- [ ] ✅ Mock data only (no real personal information)
- [ ] ✅ Production configs are templated

#### **For Production Deployment:**
- [ ] 🔄 Generate new SECRET_KEY (use: `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] 🔄 Change all default passwords
- [ ] 🔄 Use environment-specific `.env` files
- [ ] 🔄 Enable HTTPS (set `SESSION_COOKIE_SECURE=true`)
- [ ] 🔄 Use production WSGI server (not Flask dev server)

## 🔑 **Secret Keys by Priority Level**

### **🔴 CRITICAL (Never expose)**
```bash
# Flask Secret Key
SECRET_KEY=your-super-secret-flask-key-change-this-in-production

# Blockchain Private Keys (for real blockchain integration)
PRIVATE_KEY=your-ethereum-private-key-never-share-this

# Admin Credentials
ADMIN_PASSWORD=change-this-secure-password

# Database Passwords
DATABASE_URL=postgresql://username:password@localhost:5432/pmis_ai
```

### **🟡 IMPORTANT (Limit access)**
```bash
# API Tokens
HUGGINGFACE_API_TOKEN=hf_your_token_here
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_CLOUD_API_KEY=your-google-cloud-key

# External Service IDs
INFURA_PROJECT_ID=your-infura-project-id
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
```

### **🟢 SAFE (Can be public)**
```bash
# Model Configuration
AI_MODEL_NAME=all-MiniLM-L6-v2
PORT=8080
LOG_LEVEL=INFO
```

## 🛡️ **Security Best Practices**

### **1. Environment Setup**
```bash
# Copy template and customize
cp .env.template .env

# Set secure permissions (Unix/Linux/Mac)
chmod 600 .env

# Verify .env is ignored by Git
git status  # .env should NOT appear in untracked files
```

### **2. Generate Secure Keys**
```bash
# Generate Flask secret key
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generate admin password
python -c "import secrets; import string; chars=string.ascii_letters+string.digits+'!@#$%^&*'; print('ADMIN_PASSWORD=' + ''.join(secrets.choice(chars) for _ in range(20)))"
```

### **3. Production Security**
```bash
# Set secure environment variables (Linux/Mac)
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export ADMIN_PASSWORD="$(openssl rand -base64 32)"

# For Windows PowerShell
$env:SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
```

## 🔍 **Security Audit Checklist**

### **Before Git Push:**
- [ ] Run: `git status` - ensure no `.env` files
- [ ] Run: `grep -r "SECRET_KEY\|password\|token" *.py` - no hardcoded secrets
- [ ] Run: `grep -r "localhost\|127.0.0.1" *.py` - no hardcoded hosts
- [ ] Check: All sensitive files in `.gitignore`

### **Before Production:**
- [ ] New SECRET_KEY generated
- [ ] All default passwords changed
- [ ] HTTPS enabled (`SESSION_COOKIE_SECURE=true`)
- [ ] Rate limiting configured
- [ ] Logging enabled and secured
- [ ] Backup encryption enabled

## 🚨 **What to Do If Secrets Are Exposed**

### **If you accidentally commit secrets:**
1. **Immediately rotate** all exposed credentials
2. **Force push** with secrets removed: `git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env' --prune-empty --tag-name-filter cat -- --all`
3. **Contact platform administrators** (GitHub, GitLab, etc.)
4. **Monitor** for unauthorized access

### **Prevention:**
```bash
# Add pre-commit hook
echo "#!/bin/bash\nif git diff --cached --name-only | grep -q '.env'; then echo 'ERROR: .env file detected in commit. Aborting.'; exit 1; fi" > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 🎯 **Current Project Security Status**

### **✅ SECURE (Ready for Git)**
- All secrets moved to `.env` files
- Comprehensive `.gitignore` implemented
- Template files for team collaboration
- Environment variable integration
- Security documentation provided

### **📋 SECRETS THAT EXIST:**
1. **Flask SECRET_KEY**: `pmis-ai-hackathon-secret-key-2025-sih`
2. **Admin Password**: `hackathon2025`
3. **AI Model Cache**: `data/embeddings_cache.pkl` (not sensitive, but large)

### **🔄 TO CHANGE IN PRODUCTION:**
- Generate new SECRET_KEY with `secrets.token_hex(32)`
- Set strong admin password
- Enable HTTPS security headers
- Configure rate limiting
- Set up proper logging

---

## 🚀 **Quick Setup for New Team Members**

```bash
# 1. Clone repository
git clone <your-repo-url>
cd PMIS-AI-Engine

# 2. Setup environment
cp .env.template .env
# Edit .env with your values

# 3. Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Run system
python app.py
```

**🛡️ Remember: Security is not optional - it's essential for government systems!**
