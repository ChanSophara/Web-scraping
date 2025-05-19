import scrapy
import pandas as pd
from datetime import datetime

class CompanyStockSpider(scrapy.Spider):
    name = 'companies_stock_spider'
    allowed_domains = ['csx.com.kh']

    custom_settings = {
        'DOWNLOAD_DELAY': 1.0,  # Respectful crawling by setting delay between requests
    }

    def start_requests(self):
        base_url_main = "https://csx.com.kh/data/stock/daily.do?MNCD=60202&forma=ALL"
        base_url_growth = "https://csx.com.kh/data/growthdaily/listPosts.do?MNCD=60202&forma=ALL"

        companies = [
            # Main Board companies
            {"symbol": "PWSA", "issueCode": "KH1000010004", "joiningDate": "20120418", "url": base_url_main},
            {"symbol": "GTI", "issueCode": "KH1000020003", "joiningDate": "20140616", "url": base_url_main},
            {"symbol": "PPAP", "issueCode": "KH1000040001", "joiningDate": "20151209", "url": base_url_main},
            {"symbol": "PPSP", "issueCode": "KH1000050000", "joiningDate": "20160530", "url": base_url_main},
            {"symbol": "PAS", "issueCode": "KH1000060009", "joiningDate": "20170608", "url": base_url_main},
            {"symbol": "ABC", "issueCode": "KH1000100003", "joiningDate": "20200525", "url": base_url_main},
            {"symbol": "PEPC", "issueCode": "KH1000140009", "joiningDate": "20200812", "url": base_url_main},
            {"symbol": "MJQE", "issueCode": "KH1000210000", "joiningDate": "20230628", "url": base_url_main},
            {"symbol": "CGSM", "issueCode": "KH1000220009", "joiningDate": "20230627", "url": base_url_main},
            # Growth Board companies
            {"symbol": "DBDE", "issueCode": "KH1000150008", "joiningDate": "20210906", "url": base_url_growth},
            {"symbol": "JSL", "issueCode": "KH1000160007", "joiningDate": "20220210", "url": base_url_growth}
        ]

        for company in companies:
            joining_date = datetime.strptime(company['joiningDate'], '%Y%m%d').strftime('%Y%m%d')
            url = f"{company['url']}&issueCode={company['issueCode']}&fromDate={joining_date}&toDate=20240531"
            request = scrapy.Request(url, callback=self.parse)
            request.meta['company_symbol'] = company['symbol']
            yield request

    def parse(self, response):
        company_symbol = response.meta['company_symbol']
        headers = [
            'Date', 'Closing Price', 'Change', 'Trading Volume (shr)',
            'Trading Value (KHR)', 'Opening', 'High', 'Low',
            'Market Cap. (Mil.KHR)', 'Full Market Cap. (Mil.KHR)'
        ]

        # Extract the table rows
        rows = response.xpath('//div[@id="index_table"]/table[@class="summary"]//tr[position()>1]')

        data = []
        for row in rows:
            cols = row.xpath('.//td')
            col_texts = ["".join(col.xpath('.//text()').get()).strip() for col in cols]
            if len(col_texts) == len(headers):
                data.append(col_texts)
            else:
                self.logger.warning(f"Data mismatch in row: {col_texts}")

        # Create DataFrame and save to CSV
        try:
            if data:
                df = pd.DataFrame(data, columns=headers)
                file_name = f'{company_symbol}_stock_data.csv'
                df.to_csv(file_name, index=False)
                self.logger.info(f"Stock data for {company_symbol} saved to '{file_name}'")
            else:
                self.logger.error(f"No valid data found for {company_symbol}")
        except Exception as e:
            self.logger.error(f"Error creating DataFrame for {company_symbol}: {e}")

