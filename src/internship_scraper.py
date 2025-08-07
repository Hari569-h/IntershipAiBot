"""
Internship Scraper with deterministic platform order.

This module provides a structured way to scrape internships from multiple platforms
in a specific, deterministic order.
"""
import logging
from typing import List, Dict, Optional, TypedDict, Literal
from dataclasses import dataclass, asdict
import json
from datetime import datetime
from pathlib import Path

from .job_scraper import JobScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define platform types for type safety
PlatformType = Literal['linkedin']

@dataclass
class ScrapingConfig:
    """Configuration for the scraping process."""
    scraping_order: List[PlatformType] = None
    keywords: List[str] = None
    location: str = None  # No location filtering by default
    max_results: int = 100
    
    def __post_init__(self):
        """Set default values if not provided."""
        if self.scraping_order is None:
            self.scraping_order = ["linkedin"]
        if self.keywords is None:
            self.keywords = ["internship", "software", "data", "engineering"]

class ScrapingResult(TypedDict):
    """Structure for storing scraping results."""
    platform: str
    timestamp: str
    success: bool
    count: int
    error: Optional[str]
    data: List[Dict]

class InternshipScraper:
    """
    A LinkedIn-focused internship scraper.
    
    This scraper exclusively processes LinkedIn internships.
    """
    
    def __init__(self, config: Optional[ScrapingConfig] = None):
        """
        Initialize the InternshipScraper.
        
        Args:
            config: Optional configuration object. If not provided, defaults will be used.
        """
        self.config = config or ScrapingConfig()
        self.job_scraper = JobScraper()
        self.results: Dict[PlatformType, ScrapingResult] = {}
        
        # Validate scraping order
        self._validate_scraping_order()
    
    def _validate_scraping_order(self):
        """Validate that the scraping order contains only LinkedIn."""
        supported_platforms = {'linkedin'}
        for platform in self.config.scraping_order:
            if platform not in supported_platforms:
                raise ValueError(
                    f"Unsupported platform: {platform}. "
                    f"Only LinkedIn is supported."
                )
    
    def scrape_platform(self, platform: PlatformType) -> ScrapingResult:
        """
        Scrape a single platform.
        
        Args:
            platform: The platform to scrape
            
        Returns:
            ScrapingResult with the results of the operation
        """
        logger.info(f"🔍 Starting scrape: {platform.capitalize()}")
        result: ScrapingResult = {
            'platform': platform,
            'timestamp': datetime.utcnow().isoformat(),
            'success': False,
            'count': 0,
            'error': None,
            'data': []
        }
        
        try:
            # LinkedIn is the only supported platform
            method_map = {
                'linkedin': self.job_scraper.scrape_linkedin_internships
            }
            
            # Call the appropriate method
            scraped_data = method_map[platform](
                keywords=self.config.keywords,
                location=self.config.location
            )
            
            # Limit results if needed
            if self.config.max_results and len(scraped_data) > self.config.max_results:
                scraped_data = scraped_data[:self.config.max_results]
            
            result.update({
                'success': True,
                'count': len(scraped_data),
                'data': scraped_data
            })
            
            logger.info(f"✅ Completed scrape: {platform.capitalize()} "
                       f"(found {len(scraped_data)} internships)")
            
        except Exception as e:
            error_msg = str(e)
            result.update({
                'success': False,
                'error': error_msg,
                'data': []
            })
            logger.error(f"❌ Failed to scrape {platform}: {error_msg}", exc_info=True)
        
        return result
    
    def scrape_all(self) -> Dict[PlatformType, ScrapingResult]:
        """
        Scrape all platforms in the configured order.
        
        Returns:
            Dictionary mapping platform names to their scraping results
        """
        self.results = {}
        
        for platform in self.config.scraping_order:
            result = self.scrape_platform(platform)
            self.results[platform] = result
            
            # Add a small delay between platforms
            if platform != self.config.scraping_order[-1]:
                self.job_scraper.human_delay(min_sec=5, max_sec=10)
        
        return self.results
    
    def save_results(self, output_dir: str = "scraping_results"):
        """
        Save scraping results to JSON files.
        
        Args:
            output_dir: Directory to save the results
        """
        if not self.results:
            logger.warning("No results to save. Run scrape_all() first.")
            return
        
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save combined results
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        combined_file = output_path / f"combined_results_{timestamp}.json"
        
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump({k: asdict(v) for k, v in self.results.items()}, f, indent=2)
        
        logger.info(f"💾 Saved combined results to {combined_file}")
        
        # Save individual platform results
        for platform, result in self.results.items():
            platform_file = output_path / f"{platform}_results_{timestamp}.json"
            with open(platform_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(result), f, indent=2)
            
            logger.debug(f"Saved {platform} results to {platform_file}")


def main():
    """Example usage of the InternshipScraper."""
    # Create a custom configuration
    config = ScrapingConfig(
        scraping_order=["linkedin"],
        keywords=["software engineering", "data science", "machine learning"],
        location=None,  # No location filtering
        max_results=50
    )
    
    # Initialize and run the scraper
    scraper = InternshipScraper(config)
    results = scraper.scrape_all()
    
    # Save results
    scraper.save_results()
    
    # Print summary
    total_internships = sum(r['count'] for r in results.values() if r['success'])
    print(f"\n🎯 Total internships found: {total_internships}")
    for platform, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"{status} {platform.capitalize()}: {result['count']} internships")


if __name__ == "__main__":
    main()
