# Deployment Guide

This guide provides a checklist for deploying the PDF processing application to a production environment.

## Production Deployment Checklist

- [ ] Provision a server with a compatible NVIDIA GPU.
- [ ] Install NVIDIA drivers and the NVIDIA Container Toolkit.
- [ ] Install Docker and Docker Compose.
- [ ] Configure a firewall to restrict access to necessary ports only (e.g., 80, 443).
- [ ] Set up a reverse proxy (e.g., Nginx, Traefik) to handle SSL termination and load balancing.
- [ ] Configure DNS records to point to the server's IP address.

## Security Hardening

- [ ] Ensure all secrets in the `.env` file are strong and unique.
- [ ] Rotate secrets and credentials regularly.
- [ ] Configure the reverse proxy to set security headers (e.g., `Content-Security-Policy`, `Strict-Transport-Security`).
- [ ] Restrict access to the Flower dashboard to authorized users only.
- [ ] Regularly update all dependencies to patch security vulnerabilities.

## Backup and Restore Procedures

### Backup

The `backup` service in `docker-compose.yml` automatically creates daily backups of the PostgreSQL database. Backups are stored in the `./backups` directory on the host.

### Restore

To restore the database from a backup:

1. Stop the web and worker services:
   ```bash
   docker-compose stop web worker
   ```
2. Find the backup file you want to restore from in the `./backups` directory.
3. Execute the following command to restore the database:
   ```bash
   gunzip -c ./backups/<backup_file>.sql.gz | docker-compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}
   ```
4. Restart the services:
   ```bash
   docker-compose start web worker
   ```

## Monitoring and Logging

- **Application Monitoring**: Use the Flower dashboard at `http://<your_domain>:5555` to monitor Celery tasks.
- **GPU Monitoring**: Use `nvidia-smi` on the host to monitor GPU utilization.
- **Logging**: Application logs are sent to `stdout` and `stderr` and can be viewed using `docker-compose logs`.
