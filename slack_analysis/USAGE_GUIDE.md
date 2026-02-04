# Slack Channel Analysis - Quick Start Guide

## Overview

This tool analyzes 3 months of conversation history from your #dailystandup Slack channel, providing insights into:
- Team participation and engagement
- Activity patterns and trends
- Common discussion topics
- Blockers and challenges
- Overall team health indicators

## Quick Start (Easiest Method)

### 1. Set up your Slack Bot Token

**In Cursor Dashboard:**
1. Go to **Cloud Agents** → **Secrets**
2. Click **Add Secret**
3. Name: `SLACK_BOT_TOKEN`
4. Value: Your Slack Bot Token (see "Getting a Slack Bot Token" below)
5. Save

### 2. Run the analysis

```bash
cd /workspace
./slack_analysis/run_analysis.sh
```

That's it! The script will:
1. Fetch 3 months of conversations from #dailystandup
2. Analyze the data
3. Generate comprehensive reports

### 3. View the results

**Text Report:**
```bash
cat slack_analysis/analysis_report.txt
```

**Visual Charts:**
```bash
python slack_analysis/visualize_data.py
```

**Raw Data (JSON):**
```bash
cat slack_analysis/analysis_data.json
```

## Getting a Slack Bot Token

### Step 1: Create a Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name it (e.g., "Standup Analyzer")
4. Select your workspace
5. Click **"Create App"**

### Step 2: Add Permissions

1. In your app settings, go to **"OAuth & Permissions"**
2. Scroll to **"Bot Token Scopes"**
3. Add these scopes:
   - `channels:history` - View messages in public channels
   - `channels:read` - View basic channel information
   - `users:read` - View users in the workspace
   - `groups:history` - View private channel messages (if needed)
   - `groups:read` - View private channel info (if needed)

### Step 3: Install to Workspace

1. Scroll to the top of the **"OAuth & Permissions"** page
2. Click **"Install to Workspace"**
3. Review permissions and click **"Allow"**
4. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)

### Step 4: Invite Bot to Channel

In Slack, invite your bot to #dailystandup:
```
/invite @YourBotName
```

## Manual Step-by-Step Usage

If you prefer to run each step manually:

### 1. Fetch Data

```bash
cd /workspace
export SLACK_BOT_TOKEN='xoxb-your-token-here'
python slack_analysis/fetch_slack_data.py
```

This creates: `slack_analysis/conversations_data.json`

### 2. Analyze Data

```bash
python slack_analysis/analyze_conversations.py
```

This creates:
- `slack_analysis/analysis_report.txt` - Human-readable report
- `slack_analysis/analysis_data.json` - Structured data

### 3. Visualize Data (Optional)

```bash
python slack_analysis/visualize_data.py
```

Shows ASCII charts in terminal.

## What You'll Learn

### 📊 Team Activity Metrics
- How many messages were sent
- Who are the most active contributors
- Daily and weekly activity patterns
- Peak activity times

### 👥 Participation Analysis
- Individual contribution levels
- Message length and engagement quality
- Consistency of participation

### 🔤 Topic Analysis
- Most discussed topics
- Common standup keywords (accomplished, blocked, working, etc.)
- Trending words and phrases

### 💬 Engagement Metrics
- Thread reply rates
- Reaction usage
- Discussion depth and quality

### 🚧 Team Health Indicators
- Blockers and challenges mentioned
- Support needs
- Overall team momentum

### 💡 Actionable Insights
- Participation recommendations
- Engagement improvement suggestions
- Team health assessment

## Example Output

```
================================================================================
SLACK CHANNEL ANALYSIS REPORT: #dailystandup
================================================================================
Analysis Period: 2025-11-04 to 2026-02-04
Duration: 92 days

📊 BASIC STATISTICS
--------------------------------------------------------------------------------
Total Messages: 450
Human Messages: 432
Bot Messages: 18
Unique Participants: 15
Average Messages per Day: 4.89
Active Days: 68

👥 TOP CONTRIBUTORS
--------------------------------------------------------------------------------
1. John Doe - 89 messages (2,456 words, avg 27.6 words/message)
2. Jane Smith - 67 messages (1,823 words, avg 27.2 words/message)
3. Bob Johnson - 54 messages (1,345 words, avg 24.9 words/message)
...

⏰ ACTIVITY PATTERNS
--------------------------------------------------------------------------------
Peak Activity Hour: 9:00
Most Active Weekday: Monday

Messages by Weekday:
  Monday: 98 messages
  Tuesday: 76 messages
  Wednesday: 81 messages
  Thursday: 72 messages
  Friday: 65 messages
  Saturday: 3 messages
  Sunday: 5 messages

🔤 COMMON TOPICS & KEYWORDS
--------------------------------------------------------------------------------
Standup-related Keywords:
  completed: 87 mentions
  working: 156 mentions
  blocker: 12 mentions
  help: 23 mentions
  testing: 34 mentions
  ...

💬 ENGAGEMENT METRICS
--------------------------------------------------------------------------------
Messages with Thread Replies: 45
Average Replies per Thread: 3.2
Maximum Replies in a Thread: 12
Messages with Reactions: 234
Average Reactions per Message: 2.1

🚧 BLOCKERS & CHALLENGES MENTIONED
--------------------------------------------------------------------------------
1. [2026-01-15] John Doe ('blocker')
   Blocked on API integration - waiting for backend team...

2. [2026-01-20] Jane Smith ('issue')
   Issue with deployment pipeline - investigating...

💡 KEY INSIGHTS
--------------------------------------------------------------------------------
✓ High daily activity - team is actively engaged in standup
✓ Good discussion engagement - team members are following up on topics
✓ Consistent participation - most team members are posting regularly
⚠ 12 blockers/challenges mentioned - team may need support
```

## Troubleshooting

### Error: "SLACK_BOT_TOKEN environment variable not set"
**Solution:** Make sure you've added the token to Cursor Dashboard secrets or exported it in your terminal.

### Error: "Channel 'dailystandup' not found"
**Solution:** 
1. Verify the channel name is correct
2. Make sure your bot has been invited to the channel: `/invite @YourBot`

### Error: "Slack API error: missing_scope"
**Solution:**
1. Go to your app's OAuth & Permissions page
2. Add the required scopes (see "Getting a Slack Bot Token" above)
3. Reinstall the app to your workspace
4. Use the new token

### Error: "No module named 'requests'"
**Solution:** Install requests:
```bash
pip install requests
```

## Customization

### Analyze a Different Channel

Edit `fetch_slack_data.py` and change:
```python
channel_name = "dailystandup"  # Change this
```

### Adjust Time Range

Edit `fetch_slack_data.py` and change:
```python
start_date = end_date - timedelta(days=90)  # Change 90 to desired days
```

### Add Custom Keywords

Edit `analyze_conversations.py` and modify:
```python
standup_keywords = [
    "accomplished", "completed", # Add your keywords here
    # ...
]
```

## Files Generated

| File | Description | Size |
|------|-------------|------|
| `conversations_data.json` | Raw Slack messages with metadata | Variable (can be large) |
| `analysis_report.txt` | Human-readable analysis report | ~10-20 KB |
| `analysis_data.json` | Structured analysis data | ~5-15 KB |

## Privacy & Security

- **Data stays local**: All analysis happens on your machine
- **No external services**: Data is never sent to third parties
- **Bot permissions**: The bot can only read channels it's invited to
- **Token security**: Store your token securely in Cursor secrets

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the detailed README.md
3. Check the script comments for technical details

## Tips for Best Results

1. **Regular Analysis**: Run weekly or monthly to track trends
2. **Compare Periods**: Analyze different 3-month periods to see changes
3. **Share Insights**: Use reports to improve team communication
4. **Act on Findings**: Address low participation or high blocker counts
5. **Celebrate Wins**: Acknowledge top contributors and engagement

---

**Happy analyzing! 📊🚀**
