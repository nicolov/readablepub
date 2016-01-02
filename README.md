# Readablepub

Readablepub downloads a cleaned-up copy of any online article and packages it
for offline reading on many devices (as epub). Images are included, but
scripts or stylesheets aren't.

We use Readability's Parser API, so you must sign up
[here](https://www.readability.com/developers/api).

[Readlists](http://readlists.com) offers a similar (and much more 2.0) service, but I enjoy saving myself clicks when possibile. Also, one could swap the Readability API with a [Python implementation](https://github.com/buriy/python-readability) and self-host.

## Usage

```
./readablepub.py --token=YOUR_READABILITY_PARSER_TOKEN_HERE http://wwww.coolarticles.com/latest_article
```

You can also save the token under `~/.readability_parser_token` to avoid passing it in every time.
