# Universal Seinfeld Bus

![what's the deal with "little jerry seinfeld"](images/sein_what_white.png)

USB is an intentionally ambiguous acronym that describes multiple software ideas related to the hit television series "Seinfeld".

* Universal Seinfeld Bus: A USB (Universal Serial Bus) drive that can boot and play TV episodes on a PC.
* Universal Seinfeld Bibliography: A web API for querying a quote database and returning images and data about the quote.
* Universal Seinfeld Binary: A command line utility that can query the API and perform other tasks (protyped at https://github.com/progrium/usb).
* Universal Seinfeld Bot: A bot that can live in chat software (such as Discord or Slack) and respond to commands to query the API.

The only working piece at the moment is a Discord bot. You can join the Seinfeld Discord server at https://discord.gg/6z23uzH to play with it (try sending *what's the deal with "no soup for you"* in the *#whats-the-deal-with* channel).

## Local Development

Requirements:

* Kubernetes (we use [microk8s](https://microk8s.io/) in this example)
* [Skaffold](https://skaffold.dev/)

Install:

```
sudo snap install microk8s --classic
sudo snap install kubectl --classic
sudo apt install git docker.io
```


Bootstrap microk8s:

```
sudo usermod -a -G $USER docker
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube

# reload shell
microk8s.kubectl config view --raw > $HOME/.kube/config
microk8s.enable registry ingress dns
```

Start services with Skaffold:

```
skaffold dev --default-repo=localhost:32000
```

Visit the services:

* Appsearch: http://appsearch-127-0-0-1.nip.io
* Web: http://web-127-0-0-1.nip.io/search/seinfeld/yada
* Flower: http://flower-127-0-0-1.nip.io

Update secrets:

```
kubectl create secret generic appsearch --from-literal=private_key=private-53spr5yjhgfss8w3fo3upnrs
kubectl create secret generic sentry --from-literal=dsn=https://dc398d946786567bcf555aa2c1b1848@sentry.io/6785764
```

## Notes

Extract subs:

```
for file in ls **/*.mkv; do ffmpeg -i "$file" "/Users/andy/Projects/andyshinn/usb/subs/$(echo "$file" | pcregrep -io1 '(S\d{2}E\d+(E\d+)?)' | tr '[:upper:]' '[:lower:]').srt"; done
```

Index JSON:

```
for file in ls subs/*.json; do curl -X POST 'http://localhost:3002/api/as/v1/engines/usb/documents' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer private-a23c3jfz4doi7rvy1bi2xvoo' \
  --data-raw "@$file"
done
```

Rename videos:

```
for file in **/*.mkv; do cp "$file" "/Users/andy/Projects/andyshinn/usb/videos/$(echo "$file" | pcregrep -io1 '(S\d{2}E\d+(E\d+)?)' | tr '[:upper:]' '[:lower:]').mkv"; done
```
