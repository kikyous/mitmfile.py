# Define and load mitmproxy config easy

> As a web developer, I need different [mitmproxy](https://github.com/mitmproxy/mitmproxy) config (map_local, map_remote ...) per project,
with this plugin, I can define and load mitmproxy configs from .mitmproxy/Mitmfile in my project dir, use simple syntax which easy to write and read.

## Mitmfile sample
projectA/.mitmproxy/Mitmfile

```ini
view_filter !~u /static/


map_local |/api/report/17/timeline|.mitmproxy/timeline.json
map_local |/api/report/17/performance/rank|.mitmproxy/rank.json
map_local |/api/report/17$|.mitmproxy/report.json

## lives
map_local |/api/courses/.+/activities/lives|.mitmproxy/lives.json
```

when you run `mitmproxy` in projectA, It will load .mitmproxy/Mitmfile and apply all definded options.

you can use all mitmproxy config options in Mitmfile with format `key value`

comments start with '#'


## Edit
there is a `mitmfile.edit` command, which launch EDITOR to edit loaded Mitmfile file, you can do some modify, when editor exited, Mitmfile is automatic reloaded.

## Recomend config
Automatic load this plugin
```shell
$ cat ~/.mitmproxy/config.yaml
scripts:
  - ~/.mitmproxy/scripts/mitmfile.py
```

Bind "," to edit Mitmfile
```shell
$ cat ~/.mitmproxy/keys.yaml
-
  key: ","
  cmd: mitmfile.edit
```

Set `.mitmproxy` dir to global git ignore via `core.excludesfile`
```
$ cat ~/.gitignore_global
.DS_Store
.mitmproxy
```