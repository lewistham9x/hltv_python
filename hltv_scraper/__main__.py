from hltv_scraper.scraper import HLTVScraper

if __name__ == '__main__':
    scraper = HLTVScraper() 
    df = scraper.fetch_matches(limit=1)
    print(df)
