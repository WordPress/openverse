<!-- TITLE: Airflowrotation -->
<!-- SUBTITLE: To be done Weekly -->

# Instructions for weekly airflow log rotation
These instructions should become obsolete whenever the github issue #215 is resolved.  They should be considered **extemely dangerous**, and only followed if you're comfortable with linux, linux permissions, and the possibility of breaking the operating system installation on the ec2 instance that runs most of our `cccatalog` jobs.

1. Log into the EC2 instance with airflow
```
ssh ec2-user@ec2-54-85-128-241.compute-1.amazonaws.com
```
2. Change directory to `/var/lib`
```
cd /var/lib/
```
3. Change permission for `docker`
```
sudo chmod go+rX docker
```
4. Change directory to `docker`
```
cd docker
```
5. Change permission for `overlay2`
```
sudo chmod go+rX overlay2
```
6. Change directory to `overlay2`
```
cd overlay2
```
7. Change permission for `313a83827bce1a52928164126222daeefa537e3c8c9a8a68a069e5c5b7bba2fa`
```
sudo chmod go+rX 313a83827bce1a52928164126222daeefa537e3c8c9a8a68a069e5c5b7bba2fa
```

The reason for all of that is to let you run `scp` from your local machine and copy the relevant log files to your local drive (`scp` cannot use sudo).  This is assuming the drive is full (as it was this morning), and there's not room to use docker's copying functionality on the ec2 instance.  To check that permissions are properly setup, and view the log directories current state, follow steps 8 and 9.

8. Change directory to scheduler logs
```
cd /var/lib/docker/overlay2/313a83827bce1a52928164126222daeefa537e3c8c9a8a68a069e5c5b7bba2fa/merged/usr/local/airflow/logs/scheduler/
```
9. List directories
> Note:  This should show you a list of directories by date (i.e., each is named in the format `YYYY-MM-DD`)
```
ls
```

10. Back on your local machine, navigate to a directory where you'd like to store the logs
> Note: Replace `<path/to/store/logs>` with your directory to store logs
```
cd <path/to/store/logs>
```

11. Secure copy logs into local machine
> Note: Replace `<path/to/ssh/private/key>` with the private SSH key on your machine and replace `<YYYY-MM-DD>` with the desired date to copy (probably the oldest available)
```
scp -i <path/to/ssh/private/key> -r ec2-user@ec2-54-85-128-241.compute-1.amazonaws.com:/var/lib/docker/overlay2/313a83827bce1a52928164126222daeefa537e3c8c9a8a68a069e5c5b7bba2fa/merged/usr/local/airflow/logs/scheduler/<YYYY-MM-DD> .
```

Use caution, since the logs are ~650-900MB per day.  Using further `scp` commands, copy a week or two (use your judgement, and wildcards if needed) Now, it's safe to delete whatever logs you copied from the remote machine. 

12. Log back into EC2 instance with Airflow
```
ssh ec2-user@ec2-54-85-128-241.compute-1.amazonaws.com
```

13. List existing docker containers in running state
> Note: Make sure to copy the container id of airflow daemon
```
docker ps
```

14. Execute bash shell in airflow daemon's container
> Note: Replace `<container_id>` with the container id of airflow daemon
```
docker exec -it <container_id> /bin/bash
```

15. Within the container, change directory to scheduler logs
```
cd /usr/local/airflow/logs/scheduler/
```
16. Remove the directories and their contents recursively (Use caution, obviously)
> Note: Replace `<YYYY-MM-DD>` with the dates that you used in step 11
```
rm -r <YYYY-MM-DD>
``` 

Finally, you need to reset permissions on the directories you changed earlier (this is important for security; our api keys are all over these logs)

17. Exit the container (if you're still in there)
```
exit
```

You should now be `ssh`ed into the ec2 instance, but not logged into the container.

18. Change directory to `/var/lib/docker/overlay2/`
```
cd /var/lib/docker/overlay2/
```

19. Change permission for `313a83827bce1a52928164126222daeefa537e3c8c9a8a68a069e5c5b7bba2fa`
> Note: `go` is **essential** here.  It's not clear what will happen if you remove read permissions from a directory for all users including `root` 
```
sudo chmod go-rX 313a83827bce1a52928164126222daeefa537e3c8c9a8a68a069e5c5b7bba2fa
```

20. Move up one level from current directory
```
cd ..
```

21. Change permision for `overlay2`
```
sudo chmod go-rX overlay2
```

22. Move up one level from current directory
```
cd ..
```

23. Change permission for `docker`
```
sudo chmod go-rX docker
```

<br/>

Hope against hope that you have not messed anything related to permission up, since this would likely break the `docker` daemon, and perhaps the OS installation on the EC2 instance itself.
