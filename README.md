# Semitone-API
A containerized FastAPI service that exposes the semitone Python package via
a public API for querying musical relationships.

Deployed at [semitone-api.fly.dev](https://semitone-api.fly.dev).

Root library at
[github.com/mbdeaton/semitone](https://github.com/mbdeaton/semitone).

## Quick start
```bash
# Frequencies of various scales in various keys
curl https://semitone-api.fly.dev/scales/major/C
curl https://semitone-api.fly.dev/scales/minor/Bflat
curl https://semitone-api.fly.dev/scales/chromatic/F

# With query params
curl "https://semitone-api.fly.dev/scales/major/C?octaves_above=2"
```
