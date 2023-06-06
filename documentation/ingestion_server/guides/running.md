# Running on the Host

1. Create environment variables from the template file.
```
just env
```

2. Install Python dependencies
```
just install
```

3. Start the Gunicorn server.
```
pipenv run gunicorn
```