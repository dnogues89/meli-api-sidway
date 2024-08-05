# Linux Service Management for docker-compose

- Simplifies the setup process by enabling automatic startup and shutdown of your Docker Compose application, ensuring it runs consistently after reboots.
- Provides a standardized way to manage your application using familiar systemd commands (start, stop, restart, status), making it easier for users to operate.

## Example service

Under this folder, you may find an example on the file needed to accomplish this task.

 **Please check on the file *example-docker.service* **

## Step by step

1. Where is docker-compose file located?
 Example: `/opt/projects/Meli-api-autos/images/docker-compose.yml`

2. Path to save the service file
 Example: `/etc/systemd/system/Meli-api-autos.service`

3. Reload systemctl services folder to take new services
 Example: `systemctl daemon-reload`

4. Start the service and check if this is working properly
 Example to start: `systemctl start Meli-api-autos`
 Example to check status: `systemctl status Meli-api-autos`

5. Enable service (It means to run it at system startup)
 Example: `systemctl enable Meli-api-autos`

6. Stop the service
 Example: `systemctl stop Meli-api-autos`

7. Take a cup of coffe and enjoy automation.

