#!/usr/bin/env python3
"""
SFSU Classroom Database Scraper
Scrapes room numbers and associated links from https://classrooms.sfsu.edu/rooms
"""

import requests
import json
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional
from loguru import logger


class SFSUClassroomScraper:
    def __init__(self, base_url: str = "https://classrooms.sfsu.edu/rooms"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.rooms_data = []
        
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage."""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_room_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract room numbers and their associated links from the page."""
        rooms = []
        
        # Look for room links with class 'room-link'
        room_links = soup.find_all('a', class_='room-link')
        
        for link in room_links:
            room_text = link.get_text(strip=True)
            room_number = room_text if room_text else ""
            room_link = link.get('href')
            
            if room_number and room_link:
                # Convert relative URLs to absolute
                full_link = urljoin(self.base_url, room_link)
                rooms.append({
                    'room_number': room_number,
                    'link': full_link
                })
                logger.debug(f"Found room: {room_number} -> {full_link}")
        
        return rooms
    
    def scrape_all_rooms(self) -> List[Dict[str, str]]:
        """Scrape all rooms from the classroom database."""
        logger.info("Starting SFSU classroom database scrape...")
        
        # Fetch the main page
        soup = self.fetch_page(self.base_url)
        if not soup:
            logger.error("Failed to fetch main page")
            return []
        
        # Extract room data
        rooms = self.extract_room_links(soup)
        
        # Look for pagination or additional pages
        pagination_links = soup.find_all('a', href=re.compile(r'page|next|more'))
        for link in pagination_links:
            href = link.get('href')
            if href:
                page_url = urljoin(self.base_url, href)
                logger.info(f"Found pagination link: {page_url}")
                
                # Add delay to be respectful
                time.sleep(1)
                
                page_soup = self.fetch_page(page_url)
                if page_soup:
                    page_rooms = self.extract_room_links(page_soup)
                    rooms.extend(page_rooms)
        
        # Remove duplicates based on room number
        unique_rooms = {}
        for room in rooms:
            room_num = room['room_number']
            if room_num not in unique_rooms:
                unique_rooms[room_num] = room
        
        final_rooms = list(unique_rooms.values())
        logger.info(f"Scraped {len(final_rooms)} unique rooms")
        
        return final_rooms
    
    def save_to_json(self, rooms: List[Dict[str, str]], filename: str = "sfsu_classrooms.json"):
        """Save room data to a JSON file."""
        output_data = {
            "source": "https://classrooms.sfsu.edu/rooms",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_rooms": len(rooms),
            "rooms": rooms
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(rooms)} rooms to {filename}")
        except Exception as e:
            logger.error(f"Error saving to {filename}: {e}")
    
    def run(self, output_file: str = "sfsu_classrooms.json"):
        """Run the complete scraping process."""
        rooms = self.scrape_all_rooms()
        if rooms:
            self.save_to_json(rooms, output_file)
            return rooms
        else:
            logger.error("No rooms found")
            return []


def main():
    """Main function to run the scraper."""
    scraper = SFSUClassroomScraper()
    rooms = scraper.run()
    
    if rooms:
        print(f"\nScraping completed successfully!")
        print(f"Found {len(rooms)} rooms")
        print(f"Sample rooms:")
        for room in rooms[:5]:
            print(f"  {room['room_number']}: {room['link']}")
        if len(rooms) > 5:
            print(f"  ... and {len(rooms) - 5} more")
    else:
        print("Scraping failed - no rooms found")


if __name__ == "__main__":
    main()
