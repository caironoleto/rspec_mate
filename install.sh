#!/bin/sh

# Dummy
echo 'Installing RSpec Mate...'

# Copy plugin to Gedit folder
mkdir -p ~/.gnome2/gedit/plugins/rspec_mate

cp rspec_mate/__init__.py ~/.gnome2/gedit/plugins/rspec_mate
cp rspec_mate.gedit-plugin ~/.gnome2/gedit/plugins

# Ask for Python-Webkit package
sudo apt-get install python-webkit

# Dummy
echo 'Done!'

