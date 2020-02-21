
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
