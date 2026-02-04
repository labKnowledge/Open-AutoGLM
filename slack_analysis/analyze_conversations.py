#!/usr/bin/env python3
"""
Script to analyze Slack conversations from the dailystandup channel.
Provides insights on team activity, engagement, common topics, and trends.
"""

import json
import re
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Any
import statistics


class SlackConversationAnalyzer:
    """Analyzes Slack conversation data."""
    
    def __init__(self, data_file: str):
        """Initialize with conversation data file."""
        with open(data_file, 'r') as f:
            self.data = json.load(f)
        
        self.messages = self.data.get("messages", [])
        self.channel = self.data.get("channel", "")
        self.start_date = datetime.fromisoformat(self.data["start_date"])
        self.end_date = datetime.fromisoformat(self.data["end_date"])
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the conversations."""
        total_messages = len(self.messages)
        
        # Filter out bot messages
        human_messages = [m for m in self.messages if not m.get("bot_id")]
        
        # Get unique users
        unique_users = set()
        for msg in human_messages:
            if msg.get("user"):
                unique_users.add(msg.get("user"))
        
        # Calculate average messages per day
        days = (self.end_date - self.start_date).days
        avg_messages_per_day = total_messages / days if days > 0 else 0
        
        return {
            "total_messages": total_messages,
            "human_messages": len(human_messages),
            "bot_messages": total_messages - len(human_messages),
            "unique_users": len(unique_users),
            "date_range_days": days,
            "avg_messages_per_day": round(avg_messages_per_day, 2)
        }
    
    def get_user_participation(self) -> List[Dict[str, Any]]:
        """Analyze user participation."""
        user_stats = defaultdict(lambda: {
            "message_count": 0,
            "word_count": 0,
            "avg_message_length": 0
        })
        
        for msg in self.messages:
            if msg.get("user") and not msg.get("bot_id"):
                user_id = msg.get("user")
                user_info = msg.get("user_info", {})
                
                text = msg.get("text", "")
                word_count = len(text.split())
                
                if user_id not in user_stats:
                    user_stats[user_id]["name"] = user_info.get("real_name", "Unknown")
                    user_stats[user_id]["display_name"] = user_info.get("display_name", "Unknown")
                
                user_stats[user_id]["message_count"] += 1
                user_stats[user_id]["word_count"] += word_count
        
        # Calculate averages
        for user_id, stats in user_stats.items():
            if stats["message_count"] > 0:
                stats["avg_message_length"] = round(
                    stats["word_count"] / stats["message_count"], 2
                )
        
        # Sort by message count
        sorted_users = sorted(
            user_stats.items(),
            key=lambda x: x[1]["message_count"],
            reverse=True
        )
        
        return [
            {"user_id": uid, **stats}
            for uid, stats in sorted_users
        ]
    
    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in conversations."""
        messages_by_day = defaultdict(int)
        messages_by_hour = defaultdict(int)
        messages_by_weekday = defaultdict(int)
        
        for msg in self.messages:
            if "datetime" in msg:
                dt = datetime.fromisoformat(msg["datetime"])
                
                # By day
                day_key = dt.strftime("%Y-%m-%d")
                messages_by_day[day_key] += 1
                
                # By hour
                messages_by_hour[dt.hour] += 1
                
                # By weekday
                weekday = dt.strftime("%A")
                messages_by_weekday[weekday] += 1
        
        # Find peak activity times
        peak_hour = max(messages_by_hour.items(), key=lambda x: x[1])[0] if messages_by_hour else 0
        peak_day = max(messages_by_weekday.items(), key=lambda x: x[1])[0] if messages_by_weekday else "Unknown"
        
        # Calculate average messages per weekday
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_stats = [
            {"weekday": day, "count": messages_by_weekday.get(day, 0)}
            for day in weekday_order
        ]
        
        return {
            "peak_hour": peak_hour,
            "peak_weekday": peak_day,
            "messages_by_weekday": weekday_stats,
            "total_active_days": len(messages_by_day)
        }
    
    def extract_keywords_and_topics(self) -> Dict[str, Any]:
        """Extract common keywords and topics from conversations."""
        # Common standup-related keywords to look for
        standup_keywords = [
            "accomplished", "completed", "finished", "done",
            "working", "focus", "priority", "priorities",
            "blocker", "blocked", "challenge", "issue", "problem",
            "help", "support", "need", "stuck",
            "meeting", "review", "testing", "deployment",
            "feature", "bug", "fix", "implement"
        ]
        
        keyword_counts = Counter()
        all_words = []
        
        for msg in self.messages:
            text = msg.get("text", "").lower()
            
            # Remove URLs and special characters
            text = re.sub(r'http\S+', '', text)
            text = re.sub(r'<[^>]+>', '', text)  # Remove Slack formatting
            
            words = re.findall(r'\b\w+\b', text)
            all_words.extend(words)
            
            # Count standup keywords
            for keyword in standup_keywords:
                if keyword in text:
                    keyword_counts[keyword] += 1
        
        # Get most common words (excluding common stop words)
        stop_words = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
                     'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
                     'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they',
                     'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one',
                     'all', 'would', 'there', 'their', 'im', 'can', 'is', 'are',
                     'was', 'were', 'been', 'has', 'had', 'did'}
        
        filtered_words = [w for w in all_words if w not in stop_words and len(w) > 3]
        most_common_words = Counter(filtered_words).most_common(20)
        
        return {
            "standup_keyword_counts": dict(keyword_counts.most_common()),
            "most_common_words": [{"word": w, "count": c} for w, c in most_common_words]
        }
    
    def analyze_engagement(self) -> Dict[str, Any]:
        """Analyze engagement metrics."""
        thread_counts = []
        reaction_counts = []
        
        for msg in self.messages:
            # Thread replies
            reply_count = msg.get("reply_count", 0)
            if reply_count > 0:
                thread_counts.append(reply_count)
            
            # Reactions
            reactions = msg.get("reactions", [])
            if reactions:
                total_reactions = sum(r.get("count", 0) for r in reactions)
                reaction_counts.append(total_reactions)
        
        return {
            "messages_with_threads": len(thread_counts),
            "avg_replies_per_thread": round(statistics.mean(thread_counts), 2) if thread_counts else 0,
            "max_replies_in_thread": max(thread_counts) if thread_counts else 0,
            "messages_with_reactions": len(reaction_counts),
            "avg_reactions_per_message": round(statistics.mean(reaction_counts), 2) if reaction_counts else 0
        }
    
    def identify_blockers_and_challenges(self) -> List[Dict[str, Any]]:
        """Identify messages mentioning blockers or challenges."""
        blocker_keywords = [
            "blocker", "blocked", "challenge", "issue", "problem",
            "stuck", "difficult", "struggling", "error", "failure"
        ]
        
        blocker_messages = []
        
        for msg in self.messages:
            text = msg.get("text", "").lower()
            user_info = msg.get("user_info", {})
            
            for keyword in blocker_keywords:
                if keyword in text:
                    blocker_messages.append({
                        "date": msg.get("datetime", ""),
                        "user": user_info.get("real_name", "Unknown"),
                        "text": msg.get("text", "")[:200],  # First 200 chars
                        "keyword": keyword
                    })
                    break
        
        return blocker_messages[:20]  # Return top 20
    
    def generate_report(self) -> str:
        """Generate a comprehensive analysis report."""
        print("Analyzing conversations...")
        
        basic_stats = self.get_basic_stats()
        user_participation = self.get_user_participation()
        temporal_patterns = self.analyze_temporal_patterns()
        keywords_topics = self.extract_keywords_and_topics()
        engagement = self.analyze_engagement()
        blockers = self.identify_blockers_and_challenges()
        
        report = []
        report.append("=" * 80)
        report.append(f"SLACK CHANNEL ANALYSIS REPORT: #{self.channel}")
        report.append("=" * 80)
        report.append(f"Analysis Period: {self.start_date.date()} to {self.end_date.date()}")
        report.append(f"Duration: {basic_stats['date_range_days']} days")
        report.append("")
        
        # Basic Statistics
        report.append("📊 BASIC STATISTICS")
        report.append("-" * 80)
        report.append(f"Total Messages: {basic_stats['total_messages']}")
        report.append(f"Human Messages: {basic_stats['human_messages']}")
        report.append(f"Bot Messages: {basic_stats['bot_messages']}")
        report.append(f"Unique Participants: {basic_stats['unique_users']}")
        report.append(f"Average Messages per Day: {basic_stats['avg_messages_per_day']}")
        report.append(f"Active Days: {temporal_patterns['total_active_days']}")
        report.append("")
        
        # User Participation
        report.append("👥 TOP CONTRIBUTORS")
        report.append("-" * 80)
        for i, user in enumerate(user_participation[:10], 1):
            report.append(
                f"{i}. {user['name']} - {user['message_count']} messages "
                f"({user['word_count']} words, avg {user['avg_message_length']} words/message)"
            )
        report.append("")
        
        # Temporal Patterns
        report.append("⏰ ACTIVITY PATTERNS")
        report.append("-" * 80)
        report.append(f"Peak Activity Hour: {temporal_patterns['peak_hour']}:00")
        report.append(f"Most Active Weekday: {temporal_patterns['peak_weekday']}")
        report.append("\nMessages by Weekday:")
        for day_stat in temporal_patterns['messages_by_weekday']:
            report.append(f"  {day_stat['weekday']}: {day_stat['count']} messages")
        report.append("")
        
        # Keywords and Topics
        report.append("🔤 COMMON TOPICS & KEYWORDS")
        report.append("-" * 80)
        report.append("Standup-related Keywords:")
        for keyword, count in list(keywords_topics['standup_keyword_counts'].items())[:10]:
            report.append(f"  {keyword}: {count} mentions")
        report.append("\nMost Frequently Used Words:")
        for word_data in keywords_topics['most_common_words'][:15]:
            report.append(f"  {word_data['word']}: {word_data['count']} times")
        report.append("")
        
        # Engagement Metrics
        report.append("💬 ENGAGEMENT METRICS")
        report.append("-" * 80)
        report.append(f"Messages with Thread Replies: {engagement['messages_with_threads']}")
        report.append(f"Average Replies per Thread: {engagement['avg_replies_per_thread']}")
        report.append(f"Maximum Replies in a Thread: {engagement['max_replies_in_thread']}")
        report.append(f"Messages with Reactions: {engagement['messages_with_reactions']}")
        report.append(f"Average Reactions per Message: {engagement['avg_reactions_per_message']}")
        report.append("")
        
        # Blockers and Challenges
        if blockers:
            report.append("🚧 BLOCKERS & CHALLENGES MENTIONED")
            report.append("-" * 80)
            for i, blocker in enumerate(blockers[:10], 1):
                report.append(f"{i}. [{blocker['date'][:10]}] {blocker['user']} ('{blocker['keyword']}')")
                report.append(f"   {blocker['text']}...")
                report.append("")
        
        # Summary Insights
        report.append("💡 KEY INSIGHTS")
        report.append("-" * 80)
        
        if basic_stats['avg_messages_per_day'] > 5:
            report.append("✓ High daily activity - team is actively engaged in standup")
        else:
            report.append("⚠ Low daily activity - consider encouraging more participation")
        
        if engagement['avg_replies_per_thread'] > 2:
            report.append("✓ Good discussion engagement - team members are following up on topics")
        else:
            report.append("⚠ Limited follow-up discussions - topics may need more elaboration")
        
        participation_rate = basic_stats['human_messages'] / basic_stats['date_range_days'] / basic_stats['unique_users']
        if participation_rate > 0.8:
            report.append("✓ Consistent participation - most team members are posting regularly")
        else:
            report.append("⚠ Inconsistent participation - some team members may be less active")
        
        if len(blockers) > 0:
            report.append(f"⚠ {len(blockers)} blockers/challenges mentioned - team may need support")
        else:
            report.append("✓ Few blockers mentioned - team is progressing smoothly")
        
        report.append("")
        report.append("=" * 80)
        report.append("End of Report")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main function to run the analysis."""
    data_file = "slack_analysis/conversations_data.json"
    
    try:
        analyzer = SlackConversationAnalyzer(data_file)
        report = analyzer.generate_report()
        
        # Print report to console
        print(report)
        
        # Save report to file
        output_file = "slack_analysis/analysis_report.txt"
        with open(output_file, "w") as f:
            f.write(report)
        
        print(f"\n\nReport saved to {output_file}")
        
        # Also save JSON version of the analysis
        json_output = {
            "basic_stats": analyzer.get_basic_stats(),
            "user_participation": analyzer.get_user_participation(),
            "temporal_patterns": analyzer.analyze_temporal_patterns(),
            "keywords_topics": analyzer.extract_keywords_and_topics(),
            "engagement": analyzer.analyze_engagement(),
            "blockers": analyzer.identify_blockers_and_challenges()
        }
        
        json_file = "slack_analysis/analysis_data.json"
        with open(json_file, "w") as f:
            json.dump(json_output, f, indent=2)
        
        print(f"Detailed analysis data saved to {json_file}")
        
    except FileNotFoundError:
        print(f"Error: {data_file} not found")
        print("Please run fetch_slack_data.py first to fetch the conversations")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
