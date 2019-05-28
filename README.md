## Install
```
pip3 install .
```

## Usage

```
import subdivx

results = subdivx.search("game of thrones s01e02")

sub = results[0]

subfiles = sub.get_subtitles()

with open(subfiles[0]["filename"], 'wb') as f: 
    ...:     f.write(subfiles[0]["data"])
