# -*- coding: utf-8 -*-
"""
  Роботы для загрузки шрифтов.
"""
__author__ = 'bsdi4'

import logging
import os
try:
    import ujson as json
except ImportError:
    import json
from grab import Grab, GrabError
from grab.spider import Spider, Task


class WebFontSpider(Spider):
    """ Робот для http://webfont.ru """

    font_dir = os.path.join(os.path.dirname(__file__), 'WebFontFonts')

    def prepare(self):
        """ Директория шрифтов """
        try:
            os.makedirs(self.font_dir)
        except OSError:
            if not os.path.isdir(self.font_dir):
                raise

    def create_grab_instance(self, **kwargs):
        grab = Grab(**kwargs)
        grab.setup(user_agent_file='agents.txt')
        return grab

    def task_generator(self):
        """ Генерим таски """
        g = Grab()
        try:
            g.go('http://webfont.ru/data/allFonts.json')
        except GrabError:
            raise
        else:
            data = json.loads(g.response.body)
            for elm in data.iterkeys():
                yield Task('download', '{0}/{1}/{1}.zip'.format('http://webfonts.ru', elm))

    def task_download(self, grab, task):
        """ Загрузка """
        filename = task.url.split('/')[-1]
        path = os.path.join(self.font_dir, filename)
        if not os.path.exists(path):
            grab.response.save(path=path)


class Fonts4WebSpider(Spider):
    """ Робот для http://fonts4web.ru """

    base_url = 'http://fonts4web.ru'
    font_dir = os.path.join(os.path.dirname(__file__), 'Fonts4Web')

    def prepare(self):
        """ Директория шрифтов """
        try:
            os.makedirs(self.font_dir)
        except OSError:
            if not os.path.isdir(self.font_dir):
                raise

    def create_grab_instance(self, **kwargs):
        grab = Grab(**kwargs)
        grab.setup(user_agent_file='agents.txt')
        return grab

    def task_generator(self):
        """ Запуск таска """
        yield Task('homepage', url=self.base_url)

    def task_homepage(self, grab, task):
        """ Страницы шрифтов. """
        for elm in grab.doc.select('//div[@class="list_items"]/a/@href'):
            yield Task('font_page', url=elm.text(), disable_cache=True)

    def task_font_page(self, grab, task):
        """ Ссылки на страницы загрузки """
        elm = grab.doc.select('//a[contains(@class, "download")][1]/@href')
        yield Task('download_page', url=elm.text(), disable_cache=True)

    def task_download_page(self, grab, task):
        """ Ссылки на загрузку """
        elm = grab.doc.select('//a[contains(@class, "font_down_button")][1]/@href')
        yield Task('download', url=elm.text(), disable_cache=True)

    def task_download(self, grab, task):
        """ Загрузка """
        print 'Downloading {} ...'.format(task.url)
        filename = task.url.split('/')[-1]
        path = os.path.join(self.font_dir, filename)
        if not os.path.exists(path):
            grab.response.save(path=path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # WebFont робот
    bot_0 = WebFontSpider(thread_number=8)
    bot_0.run()
    print bot_0.render_stats()

    # Fonts4Web работ
    bot_1 = Fonts4WebSpider(thread_number=4)
    bot_1.run()
    print bot_1.render_stats()
