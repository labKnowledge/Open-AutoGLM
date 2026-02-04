# Slack Channel Analysis Tool

This tool analyzes conversations from the #dailystandup Slack channel over the past 3 months.

## Prerequisites

1. **Slack Bot Token**: You need a Slack Bot Token with the following OAuth scopes:
   - `channels:history` - View messages in public channels
   - `channels:read` - View basic channel information
   - `users:read` - View users in the workspace
   - `groups:history` - View messages in private channels (if analyzing private channels)
   - `groups:read` - View basic information about private channels

2. **Python Dependencies**: Install required packages:
   ```bash
   pip install requests
   ```

## Setup

### 1. Create a Slack App and Get Bot Token

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "Channel Analyzer") and select your workspace
4. Navigate to "OAuth & Permissions"
5. Add the required scopes listed above under "Bot Token Scopes"
6. Click "Install to Workspace" and authorize the app
7. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 2. Set the Environment Variable

In Cursor Dashboard:
- Go to Cloud Agents > Secrets
- Add a new secret:
  - Name: `SLACK_BOT_TOKEN`
  - Value: Your bot token (xoxb-...)

### 3. Invite Bot to Channel

In Slack, invite your bot to the #dailystandup channel:
```
/invite @YourBotName
```

## Usage

### Step 1: Fetch Slack Data

Run the fetch script to download the past 3 months of conversations:

```bash
cd /workspace
python slack_analysis/fetch_slack_data.py
```

This will:
- Connect to Slack using your bot token
- Fetch all messages from #dailystandup in the past 90 days
- Include thread replies and user information
- Save data to `slack_analysis/conversations_data.json`

### Step 2: Analyze Conversations

Run the analysis script to generate insights:

```bash
python slack_analysis/analyze_conversations.py
```

This will generate:
- `slack_analysis/analysis_report.txt` - Human-readable analysis report
- `slack_analysis/analysis_data.json` - Structured analysis data

## Analysis Features

The analysis provides:

### 📊 Basic Statistics
- Total messages and unique participants
- Average messages per day
- Active days count

### 👥 User Participation
- Top contributors ranked by message count
- Average message length per user
- Total word counts

### ⏰ Activity Patterns
- Peak activity hours and weekdays
- Message distribution by day of week
- Temporal trends

### 🔤 Topics & Keywords
- Common standup-related keywords
- Most frequently used words
- Topic extraction

### 💬 Engagement Metrics
- Thread reply statistics
- Reaction counts
- Discussion depth analysis

### 🚧 Blockers & Challenges
- Identified blocker mentions
- Challenge tracking
- Support needs analysis

### 💡 Key Insights
- Engagement assessment
- Participation patterns
- Team health indicators

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
...

⏰ ACTIVITY PATTERNS
--------------------------------------------------------------------------------
Peak Activity Hour: 9:00
Most Active Weekday: Monday
...
```

## Troubleshooting

### "SLACK_BOT_TOKEN environment variable not set"
- Make sure you've added the token to Cursor Dashboard secrets
- Restart the Cloud Agent session if needed

### "Channel 'dailystandup' not found"
- Verify the channel name is correct
- Ensure your bot has been invited to the channel

### "Slack API error: missing_scope"
- Check that all required OAuth scopes are added to your bot
- Reinstall the app to workspace after adding scopes

## Files

- `fetch_slack_data.py` - Fetches conversation data from Slack
- `analyze_conversations.py` - Analyzes fetched data and generates reports
- `README.md` - This file
- `conversations_data.json` - Raw conversation data (generated)
- `analysis_report.txt` - Analysis report (generated)
- `analysis_data.json` - Structured analysis data (generated)
