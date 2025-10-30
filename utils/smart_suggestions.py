# auracrypt2/utils/smart_suggestions.py
"""
Smart suggestions for improving user experience.
Provides intelligent category and username suggestions based on patterns.
"""

from typing import List, Dict, Optional
from collections import Counter
from utils.app_types import EntryData


class SmartSuggestions:
    """Intelligent suggestions for password entries."""

    # Category mapping based on common service patterns
    SERVICE_CATEGORY_MAPPING = {
        # Email services
        'email': ['gmail', 'outlook', 'yahoo', 'hotmail', 'icloud', 'protonmail'],
        'work': ['office', 'company', 'corporate', 'enterprise', 'business', 'slack', 'teams', 'zoom'],
        'finance': ['bank', 'credit', 'paypal', 'stripe', 'venmo', 'cashapp', 'wise', 'revolut'],
        'social': ['facebook', 'twitter', 'instagram', 'linkedin', 'tiktok', 'snapchat', 'discord', 'reddit'],
        'shopping': ['amazon', 'ebay', 'shop', 'store', 'buy', 'cart', 'etsy', 'alibaba'],
        'entertainment': ['netflix', 'youtube', 'spotify', 'hulu', 'disney', 'twitch', 'steam', 'playstation'],
        'cloud': ['google', 'dropbox', 'onedrive', 'icloud', 'github', 'gitlab', 'aws'],
        'utilities': ['electric', 'gas', 'water', 'internet', 'phone', 'mobile'],
        'travel': ['booking', 'airbnb', 'uber', 'lyft', 'airline', 'hotel', 'expedia'],
        'health': ['health', 'medical', 'doctor', 'hospital', 'pharmacy', 'insurance']
    }

    @classmethod
    def suggest_category(cls, service_name: str, existing_categories: Optional[List[str]] = None) -> str:
        """
        Suggest category based on service name patterns.

        Args:
            service_name: Name of the service
            existing_categories: List of existing categories for fallback

        Returns:
            Suggested category name
        """
        if not service_name:
            return "Uncategorized"

        service_lower = service_name.lower()

        # Check against category patterns
        for category, keywords in cls.SERVICE_CATEGORY_MAPPING.items():
            if any(keyword in service_lower for keyword in keywords):
                # Capitalize category name properly
                if category == 'work':
                    return 'Work'
                elif category == 'finance':
                    return 'Finance'
                elif category == 'social':
                    return 'Social'
                elif category == 'shopping':
                    return 'Shopping'
                elif category == 'entertainment':
                    return 'Entertainment'
                elif category == 'email':
                    return 'Personal'  # Email usually goes to Personal
                elif category == 'cloud':
                    return 'Work'  # Cloud services often work-related
                elif category == 'utilities':
                    return 'Personal'
                elif category == 'travel':
                    return 'Personal'
                elif category == 'health':
                    return 'Personal'

        # If no pattern matches, try to suggest from existing categories
        if existing_categories:
            # Simple fuzzy matching with existing categories
            for existing_cat in existing_categories:
                if existing_cat.lower() in service_lower or service_lower in existing_cat.lower():
                    return existing_cat

        return "Uncategorized"

    @classmethod
    def suggest_username(cls, service_name: str, existing_entries: List[EntryData]) -> str:
        """
        Suggest username based on existing entries patterns.

        Args:
            service_name: Name of the service
            existing_entries: List of existing password entries

        Returns:
            Suggested username
        """
        if not existing_entries:
            return ""

        # Get all usernames from existing entries
        usernames = [
            entry.get('username', '').strip()
            for entry in existing_entries
            if entry.get('username', '').strip()
        ]

        if not usernames:
            return ""

        # Find most common username
        username_counts = Counter(usernames)
        most_common = username_counts.most_common(1)

        if most_common:
            return most_common[0][0]

        return ""

    @classmethod
    def suggest_similar_entries(cls, service_name: str, existing_entries: List[EntryData], limit: int = 3) -> List[EntryData]:
        """
        Suggest similar entries based on service name.

        Args:
            service_name: Name of the service to find similar entries for
            existing_entries: List of existing entries
            limit: Maximum number of suggestions

        Returns:
            List of similar entries
        """
        if not service_name or not existing_entries:
            return []

        service_lower = service_name.lower()
        similar_entries = []

        # Score entries based on similarity
        entry_scores = []
        for entry in existing_entries:
            entry_service = entry.get('service', '').lower()
            score = 0

            # Exact match gets highest score
            if entry_service == service_lower:
                score = 100
            # Contains service name
            elif service_lower in entry_service or entry_service in service_lower:
                score = 50
            # Same category
            elif entry.get('category', '').lower() == cls.suggest_category(service_name).lower():
                score = 25
            # Check for common words
            else:
                service_words = set(service_lower.split())
                entry_words = set(entry_service.split())
                common_words = service_words.intersection(entry_words)
                if common_words:
                    score = len(common_words) * 10

            if score > 0:
                entry_scores.append((entry, score))

        # Sort by score and return top entries
        entry_scores.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, score in entry_scores[:limit]]

    @classmethod
    def suggest_url(cls, service_name: str) -> str:
        """
        Suggest URL based on service name.

        Args:
            service_name: Name of the service

        Returns:
            Suggested URL
        """
        if not service_name:
            return ""

        service_lower = service_name.lower().strip()

        # Common URL patterns
        url_patterns = {
            'gmail': 'https://gmail.com',
            'outlook': 'https://outlook.com',
            'yahoo': 'https://yahoo.com',
            'facebook': 'https://facebook.com',
            'twitter': 'https://twitter.com',
            'instagram': 'https://instagram.com',
            'linkedin': 'https://linkedin.com',
            'github': 'https://github.com',
            'gitlab': 'https://gitlab.com',
            'netflix': 'https://netflix.com',
            'amazon': 'https://amazon.com',
            'paypal': 'https://paypal.com',
            'spotify': 'https://spotify.com',
            'youtube': 'https://youtube.com',
            'reddit': 'https://reddit.com',
            'discord': 'https://discord.com'
        }

        # Check for exact matches
        if service_lower in url_patterns:
            return url_patterns[service_lower]

        # Check for partial matches
        for service, url in url_patterns.items():
            if service in service_lower:
                return url

        # Try to construct URL from service name
        # Remove common words that don't belong in URLs
        clean_name = service_lower.replace(' ', '').replace('app', '').replace('website', '')
        if clean_name and '.' not in clean_name:
            return f"https://{clean_name}.com"

        return ""

    @classmethod
    def get_category_suggestions(cls, existing_categories: List[str]) -> List[str]:
        """
        Get common category suggestions that are not already used.

        Args:
            existing_categories: List of existing categories

        Returns:
            List of suggested new categories
        """
        common_categories = [
            "Personal", "Work", "Finance", "Social", "Shopping",
            "Entertainment", "Education", "Health", "Travel",
            "Utilities", "Gaming", "Development", "Photography",
            "Music", "Sports", "Food", "Home", "Insurance"
        ]

        # Filter out existing categories (case-insensitive)
        existing_lower = [cat.lower() for cat in existing_categories]
        suggestions = [
            cat for cat in common_categories
            if cat.lower() not in existing_lower
        ]

        return suggestions[:10]  # Return top 10 suggestions
