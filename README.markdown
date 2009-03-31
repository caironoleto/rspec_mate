# RSpec Mate

RSpec Mate is a plugin for Gedit. This provide a window with results of spec like textmate. You can see screenshots in [Cairo'sBlog][rspec_mate_url].

RSpec Mate depends of python-webkitgtk package, if you don't use debian/ubuntu based distro, you will need install from source. The Python Webkit Home is located on http://code.google.com/p/pywebkitgtk/.

To install on a debian/ubuntu based distro just run in a terminal:

    $ sudo apt-get install python-webkitgtk
  
[Download RSpec Mate][down] and extract in ~/.gnome2/gedit/plugins.

You can install the gem syntax to see the codes more sexy ;)

    $ sudo gem install syntax

## Usage

Press Super + S to run current spec.

Press Super + R to run all specs in your project.

## TODO
  - save current spec before run (like CTRL + S) or run after save (using CTRL + S)
  - show errors in ruby when run spec (like syntax error)

## Authors

### **Cairo Noleto**

Working at [Jus Navigandi][jus]

Blog: [Cairo'sBlog][blog_url]

Twitter: [@caironoleto][twitter_url]

### **Cleiton Francisco**

Working at [Jus Navigandi][jus]

Site: [http://www.cleitonfco.com.br][cleitonfco_site]

Twitter: [@cleitonfco][cleiton_twitter_url]

[rspec_mate_url]: http://www.caironoleto.com/2009/03/28/rspec-mate-plugin-para-o-geditrspec-mate-plugin-para-o-gedit/
[down]: http://github.com/caironoleto/rspec_mate/tarball/master
[blog_url]: http://www.caironoleto.com/
[twitter_url]: http://www.twitter.com/caironoleto
[cleiton_twitter_url]: http://www.twitter.com/cleitonfco
[cleitonfco_site]: http://www.cleitonfco.com.br
[jus]: http://jus.uol.com.br/
