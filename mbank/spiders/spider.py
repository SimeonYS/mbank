import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import MbankItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class MbankSpider(scrapy.Spider):
	name = 'mbank'
	start_urls = ['https://cz.media.mbank.pl/']

	def parse(self, response):
		post_links = response.xpath('//a[@class="grid__box-1-1"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@rel="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):

		date = response.xpath('//p[@class="pr-story--text-small pr-font--condensed"]/text() | //p[@class="pr-story--text-small pr-font--condensed pr-font--sans"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="pr-story-content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=MbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
