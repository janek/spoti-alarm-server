all:
	@echo Usage:
	@echo make dependencies
	@echo make install
	@echo make virtualenv

virtualenv:
	# NB: If something is not quite right with the virtual environment then
	# just remove it and create it again with "make virtualenv".
	virtualenv -p /usr/bin/python3 virtualenv

dependencies: virtualenv
	./virtualenv/bin/pip install --upgrade -r requirements.txt

install:
	# Install the systemd service...
	# Create systemd directories
	mkdir -p ~/.config/systemd/user
	# Copy the service file to systemd directories
	cp spotify-alarm-clock.service ~/.config/systemd/user
	# Reload the systemd daemon: https://askubuntu.com/a/1143989/413683
	systemctl --user daemon-reload
	# Enable the service to start system boot (I hope)
	systemctl --user enable spotify-alarm-clock

dev:
	sudo -E ./virtualenv/bin/python keyboard_control.py

test:
	./virtualenv/bin/pytest
