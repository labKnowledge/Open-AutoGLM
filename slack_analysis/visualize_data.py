#!/usr/bin/env python3
"""
Script to create visualizations from Slack conversation analysis.
Creates simple ASCII charts that work in the terminal.
"""

import json
from typing import List, Dict, Any


def create_bar_chart(data: List[tuple], max_width: int = 50, title: str = "") -> str:
    """Create a simple ASCII bar chart."""
    if not data:
        return "No data to display"
    
    lines = []
    if title:
        lines.append(title)
        lines.append("-" * len(title))
    
    max_value = max(item[1] for item in data)
    
    for label, value in data:
        bar_width = int((value / max_value) * max_width) if max_value > 0 else 0
        bar = "█" * bar_width
        lines.append(f"{label:<20} {bar} {value}")
    
    return "\n".join(lines)


def create_timeline(messages_by_day: Dict[str, int], max_width: int = 70) -> str:
    """Create a timeline visualization of daily activity."""
    if not messages_by_day:
        return "No timeline data available"
    
    lines = []
    lines.append("Daily Activity Timeline")
    lines.append("=" * max_width)
    
    sorted_days = sorted(messages_by_day.items())
    max_messages = max(messages_by_day.values()) if messages_by_day else 1
    
    # Group by week for better visualization
    week_data = []
    current_week = []
    
    for i, (day, count) in enumerate(sorted_days):
        current_week.append(count)
        
        if len(current_week) == 7 or i == len(sorted_days) - 1:
            avg_week = sum(current_week) / len(current_week)
            week_data.append((day, avg_week))
            current_week = []
    
    # Show last 12 weeks
    for day, avg_count in week_data[-12:]:
        bar_width = int((avg_count / max_messages) * (max_width - 25))
        bar = "▓" * bar_width
        lines.append(f"{day:<12} {bar} {avg_count:.1f} avg/day")
    
    return "\n".join(lines)


def create_word_cloud_ascii(words: List[Dict[str, Any]], max_words: int = 30) -> str:
    """Create an ASCII representation of a word cloud."""
    if not words:
        return "No word data available"
    
    lines = []
    lines.append("Word Cloud (by frequency)")
    lines.append("=" * 50)
    
    # Sort by count
    sorted_words = sorted(words[:max_words], key=lambda x: x['count'], reverse=True)
    
    # Create size groups
    if sorted_words:
        max_count = sorted_words[0]['count']
        
        large = []
        medium = []
        small = []
        
        for word_data in sorted_words:
            word = word_data['word']
            count = word_data['count']
            ratio = count / max_count
            
            if ratio > 0.6:
                large.append(f"{word.upper()}({count})")
            elif ratio > 0.3:
                medium.append(f"{word.title()}({count})")
            else:
                small.append(f"{word}({count})")
        
        if large:
            lines.append("\n🔴 High Frequency:")
            lines.append("  " + "  ".join(large))
        
        if medium:
            lines.append("\n🟡 Medium Frequency:")
            lines.append("  " + "  ".join(medium))
        
        if small:
            lines.append("\n🟢 Low Frequency:")
            lines.append("  " + "  ".join(small))
    
    return "\n".join(lines)


def create_engagement_chart(engagement: Dict[str, Any]) -> str:
    """Create an engagement metrics visualization."""
    lines = []
    lines.append("Engagement Overview")
    lines.append("=" * 50)
    
    metrics = [
        ("Threaded Messages", engagement.get('messages_with_threads', 0)),
        ("Avg Replies/Thread", engagement.get('avg_replies_per_thread', 0)),
        ("Messages with Reactions", engagement.get('messages_with_reactions', 0)),
        ("Avg Reactions/Message", engagement.get('avg_reactions_per_message', 0))
    ]
    
    for label, value in metrics:
        if isinstance(value, float):
            lines.append(f"  {label:<25} {value:.2f}")
        else:
            lines.append(f"  {label:<25} {value}")
    
    return "\n".join(lines)


def main():
    """Main function to create visualizations."""
    data_file = "slack_analysis/analysis_data.json"
    
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        print("\n" + "=" * 80)
        print("SLACK CONVERSATION DATA VISUALIZATIONS")
        print("=" * 80 + "\n")
        
        # User participation chart
        user_participation = data.get('user_participation', [])
        if user_participation:
            top_users = [
                (user['name'][:15], user['message_count'])
                for user in user_participation[:10]
            ]
            print(create_bar_chart(top_users, title="Top 10 Contributors by Message Count"))
            print("\n")
        
        # Activity by weekday
        temporal = data.get('temporal_patterns', {})
        weekday_data = temporal.get('messages_by_weekday', [])
        if weekday_data:
            weekday_chart = [
                (day['weekday'][:3], day['count'])
                for day in weekday_data
            ]
            print(create_bar_chart(weekday_chart, title="Messages by Weekday"))
            print("\n")
        
        # Word cloud
        keywords = data.get('keywords_topics', {})
        common_words = keywords.get('most_common_words', [])
        if common_words:
            print(create_word_cloud_ascii(common_words))
            print("\n")
        
        # Standup keywords
        standup_keywords = keywords.get('standup_keyword_counts', {})
        if standup_keywords:
            keyword_chart = [
                (word, count)
                for word, count in list(standup_keywords.items())[:10]
            ]
            print(create_bar_chart(keyword_chart, title="Standup Keywords Frequency"))
            print("\n")
        
        # Engagement metrics
        engagement = data.get('engagement', {})
        if engagement:
            print(create_engagement_chart(engagement))
            print("\n")
        
        # Summary stats
        basic_stats = data.get('basic_stats', {})
        if basic_stats:
            print("=" * 50)
            print("SUMMARY STATISTICS")
            print("=" * 50)
            print(f"  Total Messages: {basic_stats.get('total_messages', 0)}")
            print(f"  Unique Users: {basic_stats.get('unique_users', 0)}")
            print(f"  Days Analyzed: {basic_stats.get('date_range_days', 0)}")
            print(f"  Avg Messages/Day: {basic_stats.get('avg_messages_per_day', 0):.2f}")
            print(f"  Active Days: {temporal.get('total_active_days', 0)}")
            print("=" * 50)
        
        print("\n✅ Visualizations complete!")
        print("For more detailed analysis, see slack_analysis/analysis_report.txt\n")
        
    except FileNotFoundError:
        print(f"Error: {data_file} not found")
        print("Please run the analysis first:")
        print("  python slack_analysis/analyze_conversations.py")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
