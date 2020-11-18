<!-- TITLE: Airflowrotation -->
<!-- SUBTITLE: To be done Weekly -->

# Instructions for weekly airflow log rotation
These instructions should become obsolete whenever the github issue #215 is resolved.  They should be considered **extemely dangerous**, and only followed if you're comfortable with linux, linux permissions, and the possibility of breaking the operating system installation on the ec2 instance that runs most of our `cccatalog` jobs.

1. `ssh` into the ec2 instance with airflow.
2. `cd /var/lib/`
3. `sudo chmod go+rX docker`
4. `cd docker`
5. `sudo chmod go+rX overlay2`
6. `cd overlay2`
7. `sudo chmod go+rX 313a83827bce1a52928164126222daeefa537e3c8c9a8a68a069e5c5b7bba2fa`

The reason for all of that is to let you run `scp` from your local machine and copy the relevant log files to your local drive (`scp` cannot use sudo).  This is assuming the drive is full (as it was this morning), and there's not room to use docker's copying functionality on the ec2 instance.  To check that permissions are properly setup, and view the log directories current state, run

8. `cd /var/lib/docker/overlay2/313a83827bce1a52928164126222daeefa537e3c8c9a8a68a069e5c5b7bba2fa/merged/usr/local/airflow/logs/scheduler/`
9. `ls`

 This should show you a list of directories by date (i.e., each is named in the format `YYYY-MM-DD`.  Next, **back on your local machine**, navigate to a directory where you'd like to store the logs, and run

```
scp -i "~/.ssh/id_rsa" -r ec2-user@ec2-54-85-128-241.compute-1.amazonaws.com:/var/lib/docker/overlay2/313a83827bce1a52928164126222daeefa537e3c8c9a8a68a069e5c5b7bba2fa/merged/usr/local/airflow/logs/scheduler/YYYY-MM-DD .
```

Note that `~/.ssh/id_rsa` should be replaced with the path to the appropriate ssh private key on your machine, and `YYYY-MM-DD` should be the desired date to copy (probably the oldest available).  Use caution, since the logs are ~650-900MB per day.  Using further `scp` commands, copy a week or two (use your judgement, and wildcards if needed) Now, it's safe to delete whatever logs you copied from the remote machine.  To do so, continue

11. `ssh` back into the ec2 instance.
12. `docker ps` (take note of the container id which has the airflow daemon.
13. `docker exec -it CONTAINER_ID /bin/bash` (replace CONTAINER_ID with the appropriate container id)
14. Within the container, `cd /usr/local/airflow/logs/scheduler/`
15. Now, for the dates you downloaded, run `rm -r YYYY-MM-DD` (use caution, obviously).

Finally, you need to reset permissions on the directories you changed earlier (this is important for security; our api keys are all over these logs)

16. exit the container (if you're still in there).  You should now be `ssh`ed into the ec2 instance, but not logged into the container.
17. `cd /var/lib/docker/overlay2/`
18. `sudo chmod go-rX 313a83827bce1a52928164126222daeefa537e3c8c9a8a68a069e5c5b7bba2fa` (`go` is **essential** here.  It's not clear what will happen if you remove read permissions from a directory for all users including `root`).
19. `cd ..`
20. `sudo chmod go-rX overlay2`
21. `cd ..`
22. `sudo chmod go-rX docker`
23. Hope against hope that you have not messed anything related to permission up, since this would likely break the `docker` daemon, and perhaps the OS installation on the ec2 instance itself.
