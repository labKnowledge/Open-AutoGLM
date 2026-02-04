#!/usr/bin/env python3
"""
Script to fetch Slack channel conversations from the past 3 months.
Requires SLACK_BOT_TOKEN environment variable to be set.
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests


class SlackDataFetcher:
    """Fetches conversation data from a Slack channel."""
    
    def __init__(self, token: str):
        """Initialize with Slack Bot Token."""
        self.token = token
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_channel_id(self, channel_name: str) -> str:
        """Get channel ID from channel name."""
        url = f"{self.base_url}/conversations.list"
        params = {"types": "public_channel,private_channel"}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("ok"):
            raise Exception(f"Slack API error: {data.get('error')}")
        
        for channel in data.get("channels", []):
            if channel["name"] == channel_name:
                return channel["id"]
        
        raise Exception(f"Channel '{channel_name}' not found")
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information from user ID."""
        url = f"{self.base_url}/users.info"
        params = {"user": user_id}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("ok"):
            return {"real_name": "Unknown User", "display_name": "Unknown"}
        
        user = data.get("user", {})
        profile = user.get("profile", {})
        
        return {
            "real_name": profile.get("real_name", "Unknown"),
            "display_name": profile.get("display_name", "Unknown"),
            "email": profile.get("email", "")
        }
    
    def fetch_channel_history(
        self, 
        channel_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch channel history between start_date and end_date."""
        url = f"{self.base_url}/conversations.history"
        
        oldest = start_date.timestamp()
        latest = end_date.timestamp()
        
        messages = []
        cursor = None
        
        while True:
            params = {
                "channel": channel_id,
                "oldest": oldest,
                "latest": latest,
                "limit": 1000
            }
            
            if cursor:
                params["cursor"] = cursor
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                raise Exception(f"Slack API error: {data.get('error')}")
            
            messages.extend(data.get("messages", []))
            
            cursor = data.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        return messages
    
    def fetch_thread_replies(self, channel_id: str, thread_ts: str) -> List[Dict[str, Any]]:
        """Fetch all replies in a thread."""
        url = f"{self.base_url}/conversations.replies"
        params = {
            "channel": channel_id,
            "ts": thread_ts
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("ok"):
            return []
        
        return data.get("messages", [])
    
    def enrich_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich messages with user information."""
        user_cache = {}
        enriched_messages = []
        
        for message in messages:
            user_id = message.get("user")
            
            if user_id and user_id not in user_cache:
                try:
                    user_cache[user_id] = self.get_user_info(user_id)
                except Exception as e:
                    print(f"Warning: Could not fetch user info for {user_id}: {e}")
                    user_cache[user_id] = {
                        "real_name": "Unknown",
                        "display_name": "Unknown",
                        "email": ""
                    }
            
            enriched_message = message.copy()
            if user_id:
                enriched_message["user_info"] = user_cache.get(user_id, {})
            
            # Convert timestamp to readable format
            if "ts" in message:
                ts = float(message["ts"])
                enriched_message["datetime"] = datetime.fromtimestamp(ts).isoformat()
            
            enriched_messages.append(enriched_message)
        
        return enriched_messages


def main():
    """Main function to fetch Slack data."""
    # Get Slack token from environment
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        print("Error: SLACK_BOT_TOKEN environment variable not set")
        print("Please set your Slack Bot Token in Cursor Dashboard (Cloud Agents > Secrets)")
        sys.exit(1)
    
    channel_name = "dailystandup"
    
    # Calculate date range (last 3 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print(f"Fetching conversations from #{channel_name}")
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    
    # Initialize fetcher
    fetcher = SlackDataFetcher(slack_token)
    
    try:
        # Get channel ID
        print("Getting channel ID...")
        channel_id = fetcher.get_channel_id(channel_name)
        print(f"Channel ID: {channel_id}")
        
        # Fetch messages
        print("Fetching messages...")
        messages = fetcher.fetch_channel_history(channel_id, start_date, end_date)
        print(f"Found {len(messages)} messages")
        
        # Fetch thread replies for threaded messages
        print("Fetching thread replies...")
        all_messages = []
        for message in messages:
            all_messages.append(message)
            
            # If message has replies, fetch them
            if message.get("reply_count", 0) > 0:
                thread_ts = message.get("ts")
                replies = fetcher.fetch_thread_replies(channel_id, thread_ts)
                # Skip first message (parent) as it's already included
                all_messages.extend(replies[1:])
        
        print(f"Total messages including replies: {len(all_messages)}")
        
        # Enrich messages with user info
        print("Enriching messages with user information...")
        enriched_messages = fetcher.enrich_messages(all_messages)
        
        # Save to file
        output_file = "slack_analysis/conversations_data.json"
        os.makedirs("slack_analysis", exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump({
                "channel": channel_name,
                "channel_id": channel_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "message_count": len(enriched_messages),
                "messages": enriched_messages
            }, f, indent=2)
        
        print(f"\nData saved to {output_file}")
        print("Ready for analysis!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
