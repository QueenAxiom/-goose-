import news

FEED = """<rss><channel>
<item><title>Older story - Reuters</title><link>https://news.google.com/a</link><pubDate>Sat, 17 Oct 2026 10:00:00 GMT</pubDate></item>
<item><title>Newest story - Reuters</title><link>https://news.google.com/b</link><pubDate>Sat, 17 Oct 2026 12:00:00 GMT</pubDate></item>
<item><title>Bad date</title><link>https://news.google.com/c</link><pubDate>nope</pubDate></item>
<item><title>Bad link - Reuters</title><link>javascript:x</link><pubDate>Sat, 17 Oct 2026 11:00:00 GMT</pubDate></item>
</channel></rss>"""


def test_sorted_newest_first_and_suffix_stripped():
    items = news.parse_feed(FEED, " - Reuters")
    assert [i["title"] for i in items] == ["Newest story", "Older story"]


def test_caps_at_max_items():
    many = "<rss><channel>" + "".join(
        f"<item><title>t{n}</title><link>https://x/{n}</link><pubDate>Sat, 17 Oct 2026 10:{n % 60:02d}:00 GMT</pubDate></item>"
        for n in range(150)) + "</channel></rss>"
    assert len(news.parse_feed(many)) == news.MAX_ITEMS
