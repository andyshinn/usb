# Universal Seinfeld Bus

![what's the deal with "little jerry seinfeld"](images/sein_what_white.png)

USB is an intentionally ambiguous acronym that describes multiple software ideas related to the hit television series "Seinfeld".

* Universal Seinfeld Bus: A USB (Universal Serial Bus) drive that can boot and play TV episodes on a PC.
* Universal Seinfeld Bibliography: A web API for querying a quote database and returning images and data about the quote.
* Universal Seinfeld Binary: A command line utility that can query the API and perform other tasks (protyped at https://github.com/progrium/usb).
* Universal Seinfeld Bot: A bot that can live in chat software (such as Discord or Slack) and respond for commands which query the API.

The only working piece at the moment is a Discord bot. You can join the Seinfeld Discord server at https://discord.gg/6z23uzH to play with it (try sending *what's the deal with "no soup for you"* in the *#whats-the-deal-with* channel).

## Local Development

Requirements:

* Docker

Run:

```
docker-compose up --build -d
```

Visit the services:

* Meilisearch: http://localhost:7700
* Web: http://localhost:5000/search/seinfeld/yada
* Flower: http://localhost:5555

## Indexing Videos

```
docker-compose run --rm worker usb cli.index-subs seinfeld "/videos/seinfeld/*.mkv"
```
