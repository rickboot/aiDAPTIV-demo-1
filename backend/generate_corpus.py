"""
Generate and save documents to disk.
Run this offline to pre-generate the corpus before running the app.

Usage:
    python3 backend/generate_corpus.py
    python3 backend/generate_corpus.py --news 100 --social 50
"""

import argparse
from pathlib import Path
from services.data_source import GeneratedDataSource
import config

def generate_corpus(news_count: int = None, social_count: int = None):
    """Generate documents and save them to disk."""
    news_count = news_count or config.GENERATED_NEWS_COUNT
    social_count = social_count or config.GENERATED_SOCIAL_COUNT
    
    print("=" * 60)
    print("GENERATING DOCUMENT CORPUS")
    print("=" * 60)
    print(f"News articles: {news_count}")
    print(f"Social signals: {social_count}")
    print()
    
    # Get data source
    data_source = GeneratedDataSource(seed=42)  # Deterministic
    
    # Setup directories
    # Default to mktg_intelligence_demo scenario (maps to ces2026 directory for backward compatibility)
    scenario_slug = "mktg_intelligence_demo"
    directory_mapping = {
        "mktg_intelligence_demo": "ces2026",  # Map scenario slug to directory name
        "intel_demo": "ces2026",  # Backward compatibility: old name
        "ces2026": "ces2026"  # Backward compatibility
    }
    directory_name = directory_mapping.get(scenario_slug, scenario_slug)
    base_dir = Path(__file__).parent.parent / "data" / "realstatic" / directory_name
    news_dir = base_dir / "news"
    social_dir = base_dir / "social"
    
    news_dir.mkdir(parents=True, exist_ok=True)
    social_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate news
    print("Generating news articles...")
    news = data_source.fetch_news(news_count)
    for article in news:
        # Sanitize filename (remove invalid chars like /)
        safe_name = article["name"].replace("/", "_").replace("\\", "_")
        filepath = news_dir / safe_name
        filepath.write_text(article["content"], encoding='utf-8')
        print(f"  ✓ {safe_name} ({article['size_kb']:.1f} KB)")
    
    print(f"\nGenerated {len(news)} news articles")
    
    # Generate social
    print("\nGenerating social signals...")
    social = data_source.fetch_social(social_count)
    for signal in social:
        # Sanitize filename (remove invalid chars like /)
        safe_name = signal["name"].replace("/", "_").replace("\\", "_")
        filepath = social_dir / safe_name
        filepath.write_text(signal["content"], encoding='utf-8')
        print(f"  ✓ {safe_name} ({signal['size_kb']:.1f} KB)")
    
    print(f"\nGenerated {len(social)} social signals")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"News articles: {len(news)}")
    print(f"Social signals: {len(social)}")
    print(f"Total new documents: {len(news) + len(social)}")
    print(f"\nFiles saved to:")
    print(f"  News: {news_dir}")
    print(f"  Social: {social_dir}")
    print("=" * 60)
    
    return len(news), len(social)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate document corpus offline")
    parser.add_argument("--news", type=int, help="Number of news articles to generate")
    parser.add_argument("--social", type=int, help="Number of social signals to generate")
    
    args = parser.parse_args()
    
    generate_corpus(news_count=args.news, social_count=args.social)
