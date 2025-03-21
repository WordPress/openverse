---
orphan: true
---

# Changelogs missing from local build

The documentation build excludes changelogs unless it is in a CI environment or
explicitly instructed to include changelogs. This significantly reduces the
number of files processed for local preview builds, which cuts startup time of
the documentation preview by half and improving the ergonomics of working with
preview documentation locally.

To force the inclusion of the changelogs, run the documentation build with
`INCLUDE_CHANGELOGS=1` in your environment. For example, the following will run
the preview build, including changelogs:

```shell
ov env INCLUDE_CHANGELOGS=1 just documentation/serve
```
