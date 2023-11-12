import scrapy
from scrapy_splash import SplashRequest
import base64

class QuoteSpider(scrapy.Spider):
    name = "quote"
    custom_settings = {
        "LOG_FILE": "quotes_to_scrape/logs/quote_spider.log",
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0"
    }

    def start_requests(self):
        url = "https://quotes.toscrape.com/"
        args={
                'html': 1, 
                'png': 1, 
                'width': 1000,
                'wait': 0.5
            }
        yield SplashRequest(url, callback=self.parse, endpoint='render.json', args=args)

    def parse(self, response):
        self.logger.info("Início do scrape")
        for quote in response.css("div.quote"):
            text = quote.css(".text::text").get()
            author = quote.css("small.author::text").get()
            tags = quote.css("a.tag::text").getall()

            yield {
                "text": text,
                "author": author,
                "tags": tags,
            }

        self.take_screenshot(response)
        self.next_page(response)


    def take_screenshot(self, response):
        self.logger.info("Tira screenshot da página")
        imgdata = base64.b64decode(response.data['png'])
        with open('splash.png', 'wb') as f:
            f.write(imgdata)
        self.logger.info("Termina de tirar screenshot da página")
    
    def next_page(self, response):
        self.logger.info("Busca da próxima página")
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            args={
                'html': 1, 
                'png': 1, 
                'width': 1000,
                'wait': 0.5
            }
            yield SplashRequest(next_page, callback=self.parse, endpoint='render.json', args=args)
        else:
            self.logger.info("Próxima página não encontrada")
