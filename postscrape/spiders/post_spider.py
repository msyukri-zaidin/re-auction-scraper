import scrapy
import re
import pandas as pd
from urllib.parse import urlparse

class PostsSpider(scrapy.Spider):
    name = "posts"
    def __init__(self, suburb='', page='', proxy='', *args, **kwargs):
        super(PostsSpider, self).__init__(*args, **kwargs)
        self.suburb = suburb
        self.page = page
        self.proxy = proxy
        
    custom_settings = {"FEEDS": {"results.csv": {"format": "csv"}}}

    def start_requests(self):
        urls = []
        if self.proxy == 'check':
            url = 'http://lumtest.com/myip.json'
            yield scrapy.Request(url=url, callback=self.parse_test)
        elif self.page == '':
            for i in range(0,30):
                url = 'http://house.speakingsame.com/p.php?q=' + self.suburb.replace(' ', '+') + '&p=' + str(i) + '&s=1&st=&type=&count=300&region=' + self.suburb.replace(' ', '+') + '&lat=0&lng=0&sta=wa&htype=&agent=0&minprice=0&maxprice=0&minbed=0&maxbed=0&minland=0&maxland=0'
                urls.append(url)
        else:
            urls = [
                'http://house.speakingsame.com/p.php?q=' + self.suburb.replace(' ', '+') + '&p=' + str(self.page) + '&s=1&st=&type=&count=300&region=' + self.suburb.replace(' ', '+') + '&lat=0&lng=0&sta=wa&htype=&agent=0&minprice=0&maxprice=0&minbed=0&maxbed=0&minland=0&maxland=0'
            ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # Connection/Proxy Test
    def parse_test(self, response):
        yield {'response': response.xpath('/html/body').get()}

    def parse(self, response):
        for entry in response.xpath('//table[@cellspacing="7"]'):
            entry_page = entry.css('.addr a::attr(href)').get()
            if entry_page is not None:
                yield scrapy.Request(response.urljoin(entry_page), callback=self.parse_house)

    def parse_house(self, response):
        all_data = {
            'address': "",
            'suburb': self.suburb,
            'price': "",
            'last_sold_date': "",
            'bedrooms': "",
            'bathrooms': "",
            'garage': "",
            'land_area': "",
            'floor_area': "",
            'build_year': "",
            'CBD_dist': "",
            'nearest_stn': "",
            'nearest_stn_dist': "",
            'nearest_pri_sch': "",
            'nearest_pri_sch_dist': "",
            'nearest_pri_sch_rank': "",
            'nearest_sec_sch': "",
            'nearest_sec_sch_dist': "",
            'nearest_sec_sch_rank': "",
            'nearest_comb_sch': "",
            'nearest_comb_sch_dist': "",
            'nearest_comb_sch_rank': "",
            'frontage': "",
            'depth': "",
            'backyard': "",
            'slope': ""
        }

        main_table = response.xpath('//table[@cellspacing="7"]')[0]
        all_data['address'] = main_table.xpath('./tr/td[1]/table/tr[1]/td/span[2]/text()').get().split(',')[0]
        price = main_table.xpath('//table/tr/td[1]/table/tr[2]/td/table/tr[1]/td/b/text()').get()
        all_data['price'] = price.lstrip('Sold $').replace(',', '')
        last_sold_date = response.xpath('//table[@cellspacing="7"]')[0].xpath('//table/tr/td[1]/table/tr[2]/td/table/tr[1]/td/text()').get()
        all_data['last_sold_date'] = last_sold_date.lstrip(' in ').rstrip('\xa0')

        for item in main_table.xpath('//table/tr/td[1]/table/tr[2]/td/table/tr'):
            element_title_list = item.xpath('./td/b/text()').getall()
            if len(element_title_list) == 1:
                element_title = element_title_list[0]
                if 'House' in element_title:
                    a = item.xpath('./td/text()').getall()
                    try:
                        all_data['bedrooms'] = a[0].strip(' ')
                        all_data['bathrooms'] = a[1].strip(' ')
                        all_data['garage'] = a[2].strip(' ')
                    except:
                        pass
                elif 'Land size' in element_title:
                    all_data['land_area'] = item.xpath('./td/text()').get().lstrip(' ').rstrip(' sqm\xa0')
                elif 'Build year' in element_title:
                    all_data['build_year'] = item.xpath('./td/text()').get().strip(' ')
                elif 'Distance' in element_title:
                    distance_list = item.xpath('./td/text()').get().split(';')
                    all_data['CBD_dist'] = distance_list[0].lstrip(' ').rstrip(' km to CBD')
                    station = distance_list[1].split('to')
                    all_data['nearest_stn_dist'] = station[0].lstrip(' ').rstrip(' km ')
                    all_data['nearest_stn'] = station[1].lstrip(' ').rstrip('\xa0')

            elif len(element_title_list) > 1:
                # Land Size | Building Size
                if 'Land size' in element_title_list[0]:
                    all_data['land_area'] = item.xpath('./td/text()')[0].get().lstrip(' ').rstrip(' sqm | ')
                if 'Building' in element_title_list[1]:
                    all_data['floor_area'] = item.xpath('./td/text()')[1].get().lstrip(' ').rstrip(' sqm\xa0')

        school_table = response.xpath('//table[@cellspacing="7"]')[2]
        school_list = school_table.xpath('./tr[3]/td/table/tr')

        nearest_pri_sch_dist = ""
        nearest_sec_sch_dist = ""
        nearest_comb_sch_dist = ""

        for i in range(1, len(school_list)):
            school_type = school_list[i].xpath('./td[2]/text()').get()
            dist = school_list[i].xpath('./td[4]/text()').get()
            try:
                if 'km' in dist:
                    dist = re.sub('[a-zA-Z ]', '', dist)
                    dist = float(dist) * 1000
                else:
                    dist = float(dist.rstrip('metres'))
                if school_type == 'Primary' and (nearest_pri_sch_dist == "" or dist < float(nearest_pri_sch_dist)):
                    all_data['nearest_pri_sch'] = school_list[i].xpath('./td[1]/a/text()').get()                    
                    all_data['nearest_pri_sch_rank'] = school_list[i].xpath('./td[3]/text()').get().lstrip('No.')
                    nearest_pri_sch_dist = dist
                elif school_type == 'Secondary'  and (nearest_sec_sch_dist == "" or dist < float(nearest_sec_sch_dist)):
                    all_data['nearest_sec_sch'] = school_list[i].xpath('./td[1]/a/text()').get()                    
                    all_data['nearest_sec_sch_rank'] = school_list[i].xpath('./td[3]/text()').get().lstrip('No.')
                    nearest_sec_sch_dist = dist
                elif school_type == 'Combined' and (nearest_comb_sch_dist == "" or dist < float(nearest_comb_sch_dist)):
                    all_data['nearest_comb_sch'] = school_list[i].xpath('./td[1]/a/text()').get()                    
                    all_data['nearest_comb_sch_rank'] = school_list[i].xpath('./td[3]/text()').get().lstrip('No.')
                    nearest_comb_sch_dist = dist
            except:
                #No school table exists
                pass

        all_data['nearest_pri_sch_dist'] = nearest_pri_sch_dist
        all_data['nearest_sec_sch_dist'] = nearest_sec_sch_dist
        all_data['nearest_comb_sch_dist'] = nearest_comb_sch_dist

        desc_table = response.xpath('//table[@cellspacing="7"]')[1]
        desc_link = desc_table.xpath('./tr[3]/td').css('a::attr(href)').get()
        if desc_link is not None:
            yield scrapy.Request(response.urljoin(desc_link), meta={'all_data': all_data}, callback=self.parse_land_desc)
        else:
            yield all_data


    def parse_land_desc(self, response):
        all_data = response.meta['all_data']
        land_desc = response.xpath('//*[@id="infoTab"]/tr')
        for desc in land_desc:
            if 'Frontage' in desc.xpath('./td/b/text()').get():
                all_data['frontage'] = desc.xpath('./td/text()').get().rstrip(' metre (width)')
            elif 'Depth' in desc.xpath('./td/b/text()').get():
                all_data['depth'] = desc.xpath('./td/text()').get().rstrip(' metre')
            elif 'Backyard' in desc.xpath('./td/b/text()').get():
                all_data['backyard'] = desc.xpath('./td/text()').get()
            elif 'Slope' in desc.xpath('./td/b/text()').get():
                all_data['slope'] = desc.xpath('./td[2]/span/b/text()').get()
        yield all_data