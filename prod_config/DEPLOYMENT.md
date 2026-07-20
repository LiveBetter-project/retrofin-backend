# Production deployment

The shared Nginx container is the only public entry point. Retrofin's frontend and
backend join its external `webproxy` Docker network without publishing host ports.
PostgreSQL stays on Retrofin's private default network only.

## First deployment

1. Ensure Docker starts after a server reboot:

   ```sh
   sudo systemctl enable --now docker
   ```

2. Confirm the shared network exists (the Nginx stack normally creates it once):

   ```sh
   docker network inspect webproxy
   ```

3. Copy `.env.prod.example` to `.env.prod`, replace all placeholders, and use the
   same random password for `DB_PASSWORD` and `POSTGRES_PASSWORD`.

4. From the Retrofin `prod_config` directory run:

   ```sh
   docker compose build --pull
   docker compose up -d
   docker compose ps
   ```

5. In the Nginx repository, validate and reload the updated Retrofin route:

   ```sh
   docker compose exec nginx nginx -t
   docker compose exec nginx nginx -s reload
   ```

6. Verify both routing targets and the public endpoint:

   ```sh
   docker network inspect webproxy --format='{{range .Containers}}{{.Name}} {{end}}'
   curl --fail https://retrofin.livebetter.epu.ntua.gr/health/
   ```


## Updating

After pulling reviewed changes, run:

```sh
docker compose build --pull
docker compose up -d --remove-orphans
docker image prune -f
```

The backend entrypoint applies committed migrations and collects static files on
each container start. Create and commit migrations during development, never at
production startup.

## Recovery 

After an unexpected reboot, verify recovery with:

```sh
systemctl status docker --no-pager
docker compose ps
docker compose logs --since=10m s342_backend s342_frontend db
curl --fail https://retrofin.livebetter.epu.ntua.gr/health/
```

An `unhealthy` status is diagnostic: Docker restart policies restart exited
processes, but Docker Compose does not automatically replace a process that is
still running yet unhealthy. Investigate its logs and use
`docker compose restart <service>` after correcting the cause.

## Backups

Back up the database before upgrades. A basic logical backup is:

```sh
docker compose exec -T db pg_dump -U s342 s342_db > s342_db.sql
```

Store automated backups outside this server. The named volume survives container
recreation, but it does not protect against disk failure or filesystem damage.
