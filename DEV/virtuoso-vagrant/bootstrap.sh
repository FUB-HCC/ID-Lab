#!/usr/bin/env bash

# install Apache
apt-get update
apt-get install -y apache2
if ! [ -L /var/www ]; then
  rm -rf /var/www
  ln -fs /vagrant /var/www
fi

# Add OpenJRE to sources
echo 'deb http://ftp.de.debian.org/debian jessie-backports main' >> /etc/apt/sources.list
# Install OpenJRE
apt-get update
apt-get install -y openjdk-8-jre

#install tomcat
apt-get install -y tomcat8

#install virtuoso
# apt-get install -y virtuoso-opensource
# only 6.1 is available as deb package!!
# manual installation:
# prerequisites:
# apt-get install -y automake -V
# apt-get install -y build-essential
# apt-get install libxml2-dev libssl-dev autoconf libgraphviz-dev libmagickcore-dev libmagickwand-dev dnsutils gawk bison flex gperf
#
wget -A deb -m -p -E -k -K -np http://de.dbpedia.org/downloads/virtuoso/7-2/
cd de.dbpedia.org/downloads/virtuoso/7-2/
# no passwords entered -> virtuoso will not run after installation
# prevent the password config
# see http://www.microhowto.info/howto/perform_an_unattended_installation_of_a_debian_package.html
apt-get install -y debconf-utils
# one can find the password keys with `sudo debconf-get-selections | grep virtuoso`
echo virtuoso-opensource-7 virtuoso-opensource-7/dba-password password root | debconf-set-selections
echo virtuoso-opensource-7 virtuoso-opensource-7/dba-password-again password root | debconf-set-selections
# install the virtuoso packages
export DEBIAN_FRONTEND=noninteractive
sudo dpkg -i *.deb
sudo apt-get -f -y install

# clean-up
cd ~/
sudo rm -rf ~/de.dbpedia.org/

# download the VAD file (Virtuoso Add-On Application Installation Packages) for the Faceted Browser (fct_dav.vad) from http://virtuoso.openlinksw.com/download/ and copy it into /usr/share/virtuoso-opensource-7/vad/
# -nv
# wget -O ~/fct_dav.vad http://opldownload.s3.amazonaws.com/uda/vad-packages/7.2/fct_dav.vad
wget http://opldownload.s3.amazonaws.com/uda/vad-packages/7.2/fct_dav.vad
mv fct_dav.vad /usr/share/virtuoso-opensource-7/vad/

# TODO: Create a webservice user account with Primary Role "dba"

# copy the GFBio db
mv /vagrant_data/virtuoso.db /var/lib/virtuoso-opensource-7/db/

# copy the GFBio app
mv /vagrant_data/GFBioRESTfulWS.war /var/lib/tomcat8/webapps/

# ---
# not needed: virtuoso is already running
# start virtuoso
# sudo service virtuoso start
# cd /var/lib/virtuoso-opensource-7/db
# sudo chown -R vagrant ./
# cd /etc/virtuoso-opensource-7/
# virtuoso-t -f -c /etc/virtuoso-opensource-7/virtuoso.ini &
# ---

# restart server
sudo service apache2 restart
sudo service tomcat8 restart
sudo /etc/init.d/virtuoso-opensource-7 restart
