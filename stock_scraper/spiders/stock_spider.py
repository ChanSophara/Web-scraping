import scrapy
import pandas as pd

class StockSpider(scrapy.Spider):
    name = "stock_spider"
    allowed_domains = ["csx.com.kh"]
    start_urls = [
        "https://csx.com.kh/data/stock/daily.do?lang=en&MNCD=60202&board_type=M&issueCode=KH1000010004&forma=ALL&fromDate=20120418&toDate=20240531"
    ]

    def parse(self, response):
        headers = [
            'Date', 'Closing Price', 'Change', 'Trading Volume (shr)',
            'Trading Value (KHR)', 'Opening', 'High', 'Low',
            'Market Cap. (Mil.KHR)', 'Full Market Cap. (Mil.KHR)'
        ]

        # Extract the table and rows
        table = response.xpath('//div[@id="index_table"]/table[@class="summary"]')
        rows = table.xpath('.//tr[position()>1]')

        data = []
        for row in rows:
            # Cleaning each column to ensure there are no extra spaces or newline characters
            cols = ["".join(col.xpath('.//text()').getall()).strip() for col in row.xpath('.//td')]
            data.append(cols)

        # Try to create DataFrame and save it
        try:
            df = pd.DataFrame(data, columns=headers)
            df.to_csv('PWSA_Scrapy_stock_prices.csv', index=False)
            self.logger.info("Stock data saved to 'PWSA_Scrapy_stock_prices.csv'")
        except Exception as e:
            self.logger.error(f"Error creating DataFrame: {e}")
