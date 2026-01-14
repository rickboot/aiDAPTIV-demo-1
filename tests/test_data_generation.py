"""
Test script to preview generated data.
Run: python3 backend/test_data_generation.py
"""

from services.data_source import get_data_source
import config

print("=" * 60)
print("DATA GENERATION TEST")
print("=" * 60)
print(f"Mode: {config.DATA_SOURCE_MODE}")
print(f"News Count: {config.GENERATED_NEWS_COUNT}")
print(f"Social Count: {config.GENERATED_SOCIAL_COUNT}")
print()

# Get data source
data_source = get_data_source()

# Generate sample news
print("GENERATING NEWS ARTICLES...")
print("-" * 60)
news = data_source.fetch_news(5)
for i, article in enumerate(news[:3], 1):
    print(f"\n[{i}] {article['name']}")
    print(f"Category: {article['category']}")
    print(f"Size: {article['size_kb']:.1f} KB")
    print(f"Preview: {article['content'][:200]}...")
    print()

# Generate sample social
print("\nGENERATING SOCIAL SIGNALS...")
print("-" * 60)
social = data_source.fetch_social(3)
for i, signal in enumerate(social, 1):
    print(f"\n[{i}] {signal['name']}")
    print(f"Platform: {signal.get('platform', 'N/A')}")
    print(f"Size: {signal['size_kb']:.1f} KB")
    print(f"Preview: {signal['content'][:200]}...")
    print()

# Show dossiers
print("\nLOADING DOSSIERS...")
print("-" * 60)
dossiers = data_source.fetch_dossiers()
print(f"Found {len(dossiers)} dossier files")
for dossier in dossiers:
    print(f"  - {dossier['name']} ({dossier['size_kb']:.1f} KB)")

print("\n" + "=" * 60)
print(f"Total News: {len(news)}")
print(f"Total Social: {len(social)}")
print(f"Total Dossiers: {len(dossiers)}")
print(f"Total Documents: {len(news) + len(social) + len(dossiers)}")
print("=" * 60)
