# Bardak: dead simple inventory management for households with too much stuff

![screenshot of bardak web interface](screenshot.png)

Bardak is a dead simple inventory management solution.

You click the big blue button to add a picture of the thing you want to catalogue,
type a description
(what it is, who owns it, and where to find it),
and then click the big red button to save.

All existing things are listed on the front page.
You can use your browser's search feature to look for specific things.
You can edit a thing's description or delete it.

## Setting up

Bardak is also dead simple to set up.
Simply clone this repository to your homeserver and run `bardak.py`.
It will serve the Bardak web interface on port 8085.
The only dependency is a relatively new version of Python,
that's it.
No packages, no modules, nothing.

If you want, you can also run Bardak in a docker container.
A sample Dockerfile and docker-compose.yml are provided.

### Access from the internet

Bardak is not secure, please do not open it up to the internet.
If you want to be able to use Bardak from outside of your home network,
either set up a VPN,
or add password protection to Bardak by running it behind a reverse proxy,
such as nginx.

## Tinkering

> Give a man a place to store data, and you will have a bug.  
> Give a man two places to store the same data,
> that need to be kept in sync,  
> and you will have AN UNLIMITED NUMBER OF BUGS.

Bardak does not use an index file or a database or anything like that.
All things are stored in the `things` directory.
Each things corresponds to a `<filename>.*` image file
and a `<filename>.txt` description.

If you want to add things to bardak without using the web interface,
simply put the image and description files into the `things`
directory, and they will show up in the web interdace.

Bardak sets `filename` to the current unix timestamp when creating new things,
but there are no strict requirements for the filename.

Deleting things causes the image and description files to be moved to
the `trash` directory.

## License

Bardak is free software: you can redistribute it and/or modify it under the
terms of the GNU Affero General Public License as published by the Free
Software Foundation, version 3 of the License only.

bardak is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License along
with bardak. If not, see <https://www.gnu.org/licenses/>. 

Note: Previous versions of bardak were released under different licenses. If
the current license does not meet your needs, you may consider using an
earlier version under the terms of its original license. You can find these
versions by browsing the commit history.

---

Copyright (c) 2025, maybetree.

