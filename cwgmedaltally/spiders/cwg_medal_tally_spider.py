# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin


# Items
class MedalsData(scrapy.Item):
    Year = scrapy.Field()
    HostCountry = scrapy.Field()
    Country = scrapy.Field()
    Gold = scrapy.Field()
    Silver = scrapy.Field()
    Bronze = scrapy.Field()
    Total = scrapy.Field()


class CwgMedalTallySpider(scrapy.Spider):
    name = 'cwg_medal_tally_spider'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/1930_British_Empire_Games']

    def parse(self, response):
        # hardcoding year_pagination table (Reason being id attribute was not populating in scrapy response object)
        pagination_table = response.css('.nowraplinks')[1]

        for a_tag in pagination_table.css('.navbox-list.navbox-odd.hlist a'):
            #get url to next evemt
            relative_url = a_tag.css('::attr(href)').extract_first()
            base_url = '/'.join(response.url.split('/')[:-1])
            absolute_url = urljoin(base_url, relative_url)
            # fetch year
            year = a_tag.css('::text').extract_first()
            meta = {'year': year}
            yield response.follow(absolute_url, self.parse_medals_page, meta=meta)


    def parse_medals_page(self, response):

        table_data = response.css('.wikitable.sortable.plainrowheaders tr')
        table_data = table_data[1:-1]  # removing header and footer row
        year = response.meta.get('year')
        for tr in table_data:
            try:
                host_country = response.css(
                    '.wikitable.sortable.plainrowheaders tr[style] td[align=left] a::text').extract_first()
                country = tr.css('td[align=left] a::text').extract_first()
                g, s, b, t = tuple(tr.css('td[align=left] ~ td::text').extract())

            except ValueError:

                try:
                    # for https://en.wikipedia.org/wiki/2006_Commonwealth_Games_medal_table
                    host_country = response.css(
                        '.wikitable.sortable.plainrowheaders tr[style] td[style] a::text').extract_first()
                    country = tr.css('td[style] a::text').extract_first()
                    g, s, b, t = tuple(tr.css('td[style] ~ td::text').extract())

                except ValueError:
                    country, g, s, b, t = 'None', 0, 0, 0, 0

            medals_feed = MedalsData()
            medals_feed['Year'] = year
            medals_feed['HostCountry'] = host_country
            medals_feed['Country'] = country
            medals_feed['Gold'] = g
            medals_feed['Silver'] = s
            medals_feed['Bronze'] = b
            medals_feed['Total'] = t

            yield medals_feed
