# Local wger setup

wger runs from the official compose files (https://github.com/wger-project/docker, AGPL-3.0),
cloned to `~/wger-docker`, with the two files in this folder added:

```bash
git clone https://github.com/wger-project/docker.git ~/wger-docker
cp docker-compose.override.yml ~/wger-docker/
cp wger-local.env ~/wger-docker/config/
cd ~/wger-docker && docker compose up -d --wait
```

- Port 8020 on this laptop only (`127.0.0.1:8020`); open http://localhost:8020
- Exercise list synced from wger.de; food database, exercise images and videos are off (disk space)
- Change the default `admin` / `adminadmin` password, create a demo client and API key, and put them in `../.env` (see `../.env.example`)
- If pages fail with "Couldn't load manifest 'staticfiles.json'": the static index was cut off (e.g. disk full).
  Delete it and rebuild: `docker compose exec web sh -c 'rm -f /home/wger/static/staticfiles.json' && docker compose exec web python3 manage.py collectstatic --no-input`
