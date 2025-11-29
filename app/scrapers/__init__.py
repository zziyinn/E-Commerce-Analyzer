"""
爬蟲模組
只保留 BeautifulSoup 爬蟲（前後端分離，統一使用 BeautifulSoup）
"""

from .base_scraper import BaseScraper
from .beautifulsoup_scraper import BeautifulSoupScraper

__all__ = [
    'BaseScraper',
    'BeautifulSoupScraper',
]
