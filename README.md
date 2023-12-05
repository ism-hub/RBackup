# What is it doing
- Backing up data
    - Based on rsync and is a dcoker image (can run with docker-compose)
    - Each backup has timestamp e.g. a valid backup can be `laptop.07-12-2023_13-32-58` (UTC time)
    - Can have 'backup-history' (multiple backups on different times, can limit the history size), each new backup hard-links againts the previos one, thus saving space.
    - Crontab already set and exposed in `/config` (via mount) to configure the exact timer
    - Backups that are currently in progress (or didn't finish yet e.g. lost-connection etc.) has the `.incomplete` suffix attached to them e.g. `laptop.07-12-2023_13-32-58.incomplete`
        - Automatically resumes incomplete updates the next time the crontab asking for an update
    - Supports 'minimum passed duration' parameter - even if the timer asks for backup it won't backup if not enough time has passed
        - This way, if the connection is bad and keep failing, the user don't need to understand that fail happened and call the script again, he can just keep asking (via the crontab timer) for backups, and the system will try to backup if incomplete and won't backup if the latest backup is 'fresh' (lower than 'minimum passed duration')
    - Supports remote sources (destination must be local (for now, till I'll need it to be remote))

# Docker compose file 

``` yaml
version: '3.2'

services:
  backup_manager:
    image: ism1/backup_manager
    environment: 
      - SRCS_TO_BACKUP= # must, what to backup e.g. /home/uname/my_config,/home/uname/Documents
      - BACKUP_NAME_PREFIX=my_backups # optional, the backups prefix
      # - REMOTE_SRC_HOST= # optional, local if not specified. form - uname@<ip/domain>[:port]
      # - RSYNC_SINGLE_PARAMS= # optional, form - '-x,-z,--relative'
      # - RSYNC_DICT_PARAMS= # optional, form - '{"key":"value"}'
      # - MAX_BACKUPS= # optional, default is 30, after MAX_BACKUPS is reached, we delete the oldest one before creaating a new one
      # Default is 20. if for some reason asking for backup before this time passed - don't do anything.
      # Always continue incomplete backups (regardless of passed time)
      # This param is useful if the backup keep faling so you can just set the crontab to be called every few mins and it will try to cont the failed (incomplete) backup
      # (but won't spam you with backups every min if one already succeeded)
      # - MINIMUM_TIME_GUARD_H=
      # - LOG_FILE= # optional, None means stdout
    volumes: 
      # - ~/servers/backup_manager/config:/config # optional mount, can edit the crontab timing and the configuration (instead of using the env vars)
      - ~/servers/backup_manager/backups:/backups # must, to where you want the backups to go
      - ~/.ssh:/root/.ssh  # needed onlt when remote-src, make sure the container can connect to the remote-src without the need of human interaction (pass, known-hosts etc. (ssh-copy-id and mount to the .ssh of the container))
      # - /:/host_fs  # if local can ssh or mount the root
    restart: unless-stopped
```

# How the backups are organized 
Theme output - 
```
ism@ismain:/.../backups$ ls -l
total 24
drwxr-xr-x+ 3 root root 4096 Oct  6 12:03 server.07-12-2023_13-32-58
drwxr-xr-x+ 3 root root 4096 Oct  6 12:03 server.07-12-2023_21-08-09
drwxr-xr-x+ 3 root root 4096 Oct  6 12:03 server.08-12-2023_21-06-31
drwxr-xr-x+ 3 root root 4096 Oct  6 12:03 server.09-12-2023_21-07-01.incomplete
```
- *server.07-12-2023_13-32-58* means we backed-up the server at Dec-7-2023,13:32:58 UTC time.

# Minimum Required Setup
- In the docker compose - 
    - Specify what you want to backup (e.g. `SRCS_TO_BACKUP=/home/uname/my_config,/home/uname/Documents`)
    - From who you want to backup (e.g. `REMOTE_SRC_HOST=exa@www.example.com:2222`)
        - Need to be able to connect to the machine without password 
            - Can use `ssh-copy-id` on the host (where the container is running) and mount the `~/.ssh` folder to the container (so it will use the host's `known-hosts` and `key`)
    - Where put the backups (volume `/backup` e.g. `~/servers/backup_manager/backups:/backups`)
- `docker compose up` and done.

# Build Image From Source
The image is docker-hub, but if you want to build it from source just run `docker compose build`

# Run Tests
cd into the test folder and execute make.
the tests are ran inside a container so no need to prep env
(only need docker compose and can use ansible script to install it, in the terminal do this -
`bash <(curl -s https://raw.githubusercontent.com/ism-hub/ansible/main/docker.sh)` )

TODOs
- Build add image to dcker-hub
- Restore script/cli of specific version
- Way to follow (maybe mail) on critical errors, currently I manually inspect the logs and FS from time to time
