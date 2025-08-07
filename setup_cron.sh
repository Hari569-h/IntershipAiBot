#!/bin/bash

# Setup script for automated internship application bot
# This script sets up a cron job to run the bot every 3 hours

echo "🤖 Setting up automated internship application bot..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📍 Project directory: $SCRIPT_DIR"

# Make the automation script executable
chmod +x "$SCRIPT_DIR/run_automation.py"

# Create the cron job entry
CRON_JOB="0 */3 * * * cd $SCRIPT_DIR && source venv/bin/activate && python run_automation.py >> logs/cron.log 2>&1"

echo "⏰ Setting up cron job to run every 3 hours..."
echo "📝 Cron job: $CRON_JOB"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "run_automation.py"; then
    echo "⚠️ Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "run_automation.py" | crontab -
fi

# Add the new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job set up successfully!"
echo "📋 Current cron jobs:"
crontab -l

echo ""
echo "🔧 Manual cron job management:"
echo "   - View cron jobs: crontab -l"
echo "   - Edit cron jobs: crontab -e"
echo "   - Remove all cron jobs: crontab -r"
echo ""
echo "📊 Monitor automation:"
echo "   - View logs: tail -f logs/automation_$(date +%Y%m%d).log"
echo "   - View cron logs: tail -f logs/cron.log"
echo ""
echo "🚀 The bot will now run automatically every 3 hours!" 