#!/usr/bin/env python3

"""
Readablepub downloads a cleaned-up copy of any online article and
packages it for offline reading on many devices (as epub).
Images are included, but scripts or stylesheets aren't.

We use Readability's Parser API, so you must sign up at:
https://www.readability.com/developers/api

"""

from __future__ import print_function
import sys, logging, os, argparse

from readability import ParserClient
from slugify import slugify
from lxml import etree
import requests

from ebooklib.utils import parse_html_string
from ebooklib.plugins.base import BasePlugin
from ebooklib import epub


class DownloadImagesPlugin(BasePlugin):
    """
    Ebooklib has nice hooks in the form of plugins. This one downloads
    all referenced images in the cleaned-up HTML and changes the src
    attributes so that they point at the local resources.
    """

    NAME = "DownloadImagesPlugin"

    def html_before_write(self, book, chapter):
        try:
            html_tree = parse_html_string(chapter.content)
        except:
            return

        for img_elem in html_tree.iterfind('.//img'):
            href = img_elem.attrib['src']
            split_href = os.path.splitext(img_elem.attrib['src'])
            # We can just slugify the original URL to determine the new URL
            img_local_filename = slugify(split_href[0]) + split_href[1]
            book.add_item(
                    epub.EpubItem(
                            uid=img_local_filename,
                            file_name=img_local_filename,
                            content=requests.get(href).content))
            # Alter the HTML element to point at the local resource
            img_elem.attrib['src'] = img_local_filename

        chapter.content = etree.tostring(html_tree, pretty_print=True,
                                         encoding='utf-8')


class ReadabilityToEpub:
    def __init__(self, parser_token=None):
        if not parser_token:
            raise Exception("Get a Readability parser token at: https://www.readability.com/developers/api")
        self.parser_client = ParserClient(token=parser_token)

    def convert_url(self, url):
        parser_resp = self.parser_client.get_article(url).json()

        epub_book = epub.EpubBook()
        epub_book.set_title(parser_resp['title'])
        epub_book.add_author(parser_resp['author'])

        content_html = epub.EpubHtml(
                title=parser_resp['title'],
                file_name='content.xhtml',
                content="<h1>{}</h1>\n{}".format(
                        parser_resp['title'],
                        parser_resp['content']))

        epub_book.add_item(content_html)
        epub_book.add_item(epub.EpubNcx())
        epub_book.add_item(epub.EpubNav())
        # A spine determines the order in which content will be shown
        epub_book.spine = [content_html]

        epub.write_epub("{}.epub".format(slugify(parser_resp['title'])),
                        epub_book,
                        dict(plugins=[DownloadImagesPlugin()]))


def main():
    parser = argparse.ArgumentParser(description="Save online articles as EPUB using the Readability API")
    parser.add_argument('url', type=str, help="URL of the article")
    parser.add_argument('--token', type=str, help="Readability API Parser token")
    args = parser.parse_args()

    if not args.token:
        token_file_name = os.path.join(os.path.expanduser('~'), '.readability_parser_token')
        try:
            token = open(token_file_name).read().strip()
        except:
            sys.exit("You did not pass a Readability parser token as argument and we couldn't read it from {}".format(
                token_file_name))
    else:
        token = args.token

    downloader = ReadabilityToEpub(parser_token=token)
    downloader.convert_url(args.url)


if __name__ == '__main__':
    main()
