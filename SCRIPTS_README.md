# 🚀 PMIS AI Allocation Engine - Scripts Guide

This guide explains how to use the shell scripts for managing the PMIS AI Allocation Engine.

## 📁 Available Scripts

### 1. `setup.sh` - Initial Setup
**Purpose**: First-time installation and environment setup

**Usage**:
```bash
./setup.sh
```

**What it does**:
- ✅ Checks Python 3 and pip installation
- ✅ Creates virtual environment
- ✅ Installs all required packages
- ✅ Creates necessary directories
- ✅ Tests installation
- ✅ Provides next steps

**When to use**: First time setup or when switching to a new machine

---

### 2. `start_server.sh` - Start Server
**Purpose**: Start the Flask server (if not already running)

**Usage**:
```bash
./start_server.sh
```

**What it does**:
- ✅ Checks if virtual environment exists
- ✅ Checks if port 5000 is available
- ✅ Activates virtual environment
- ✅ Installs missing packages (if any)
- ✅ Creates necessary directories
- ✅ Starts Flask server

**When to use**: Starting the server for the first time or after a clean shutdown

---

### 3. `restart_server.sh` - Restart Server
**Purpose**: Stop any existing server and start a fresh one

**Usage**:
```bash
./restart_server.sh
```

**What it does**:
- 🛑 Stops all Flask processes
- 🛑 Kills processes using port 5000
- 🚀 Starts a fresh Flask server
- ✅ Handles all the same checks as start_server.sh

**When to use**: After code changes, when server is stuck, or to refresh the application

---

## 🎯 Quick Commands

### First Time Setup:
```bash
chmod +x *.sh
./setup.sh
./start_server.sh
```

### Daily Usage:
```bash
# Start server
./start_server.sh

# Restart server (after changes)
./restart_server.sh
```

### Troubleshooting:
```bash
# Force restart (if server is stuck)
./restart_server.sh

# Check if server is running
curl http://localhost:5000/api/health
```

## 🌐 Server URLs

Once the server is running, you can access:

- **Main Application**: http://localhost:5000
- **Upload Page**: http://localhost:5000/upload
- **Health Check**: http://localhost:5000/api/health
- **Test Route**: http://localhost:5000/test

## 📊 Sample Data

The scripts work with the sample data in `sample_data/`:

- **50 Candidates**: `sample_data/candidates.csv`
- **50 Internships**: `sample_data/internships.csv`
- **Sample Resumes**: `sample_data/resumes/`

## 🔧 Troubleshooting

### Port Already in Use:
```bash
# Check what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use restart script
./restart_server.sh
```

### Virtual Environment Issues:
```bash
# Recreate virtual environment
rm -rf venv
./setup.sh
```

### Package Issues:
```bash
# Reinstall packages
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 Script Features

### Safety Checks:
- ✅ Python 3 installation check
- ✅ Virtual environment validation
- ✅ Port availability check
- ✅ Package installation verification

### Error Handling:
- ❌ Clear error messages
- 🔄 Automatic retry logic
- 🛑 Graceful shutdown
- 📋 Helpful next steps

### User Experience:
- 🎯 Clear status messages
- 📊 Progress indicators
- 🌐 URL display
- 📁 Directory creation

## 🚀 Advanced Usage

### Background Execution:
```bash
# Start server in background
nohup ./start_server.sh > server.log 2>&1 &

# Check server status
tail -f server.log
```

### Custom Port:
```bash
# Edit scripts to use different port
# Change --port=5000 to --port=8080
```

### Development Mode:
```bash
# Edit scripts to enable debug mode
# Add FLASK_ENV=development
```

---

**Ready to manage your PMIS AI Allocation Engine efficiently!** 🎯
