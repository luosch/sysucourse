rm app.zip
zip -r app.zip config.py server.py database.py jwxt.py
scp -P 22822 app.zip root@lsich.com:/root/sysucourse/app.zip
