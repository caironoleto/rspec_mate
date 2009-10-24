# Copyright (C) 2009 - Cairo Noleto and Cleiton Francisco
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Obtained original program from Nando Vieira and Alexandre da Silva

from gettext import gettext as _
import gedit
import gconf
import gtk
import gtk.gdk
import os
import stat
import pygtk
import webkit
import re
import gnomevfs
import subprocess
from string import Template

TMP_FILE = '/tmp/%s_rspec_mate.html' %  os.environ['USER']
OUT_FILE = '/tmp/%s_error.out' %  os.environ['USER']

ui_str = """
<ui>
    <menubar name="MenuBar">
        <menu name="ViewMenu" action="View">
            <menuitem name="RSpecOne" action="RSpecOne"/>
            <menuitem name="RSpecTwo" action="RSpecTwo"/>
        </menu>
    </menubar>
</ui>
"""

# Helper Functions

# Link Pattern (in line)
lp = re.compile('([^/]*)(((\/[a-zA-Z0-9-_\.]+)+):(\d+):)(.*)$')

# Title Pattern
tp = re.compile('.*1">([a-zA-Z0-9-_\. ]*)</dt>.*')

# Root path pattern
rp = re.compile('(.*\/spec\/).*')

# Model|Controller|View => work with rails
wrp = re.compile('(.*)\/app\/(controllers|helpers|models|views)\/(.*)(\.rb|\.erb)')
crp = re.compile('(.*)\/app\/controllers\/(.*)\_controller.rb')

def get_line(line = ''):
    output = '%s<a href="%s">%s</a>%s\n'
    result = lp.match(line)
    if result:
        line = output % (result.group(1), file_link(result.group(3), int(result.group(5))), result.group(2), result.group(6))
    return line
    
def get_file_path(uri):
    return uri.replace("file://", "")
    
def get_root_path(uri):
    result = rp.match(uri)
    if result:
      uri = result.group(1)
    return uri

def get_spec(uri):
    result = wrp.match(uri)
    if result:
      path = "%s/spec/%s/%s_spec.rb" % (result.group(1), result.group(2), result.group(3))
      if result.group(2) == 'views':
        path = "%s/spec/%s/%s.erb_spec.rb" % (result.group(1), result.group(2), result.group(3))
      if result.group(2) == 'controllers':
        result = crp.match(uri)
        if result:
          f = "%s/spec/routing/%s_routing_spec.rb" % (result.group(1), result.group(2))
          if os.path.isfile(f):
            path = path + " " + f
          else:
            f = "%s/spec/controllers/%s_routing_spec.rb" % (result.group(1), result.group(2))
            path = (path + " " + f) if os.path.isfile(f) else path
    else:
      path = uri
    return path

def get_title(title):
    result = tp.match(title)
    if result:
      title = result.group(1)
      return title
    return None
    
def file_link(file, line=0):
    return "gedit:///%s?line=%d" % (file,line)

def error_extract():
    f = open(OUT_FILE)
    mp           = re.compile("((((\/[a-zA-Z0-9-_\.]+)+):(\d+):)*)([^/]*)(((\/[a-zA-Z0-9-_\.]+)+):(\d+):)(.*)$")
    file_url     = ''
    console      = ''
    message_line = f.readline()
    result       = mp.match(message_line)
    message      = message_line
    if result:
        message = result.group(11)
        file_url = '<a href="%s">%s</a>' % (file_link(result.group(8), int(result.group(10))), result.group(7))

    for l in f.readlines():
        console += l
    html_pattern = \
"""
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html 
  PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <title>RSpec results</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Expires" content="-1" />
  <meta http-equiv="Pragma" content="no-cache" />
  <style type="text/css">
body {
  margin: 0;
  padding: 0;
  background: #fff;
  font-size: 80%;
}
#rspec-header {
  background: #797979; color: #fff; height: 4em;
}
.rspec-report h1 {
  margin: 0px 10px 0px 10px;
  padding: 10px;
  font-family: "Lucida Grande", Helvetica, sans-serif;
  font-size: 1.8em;
  position: absolute;
}
.results {
  padding:10px;
}
.failure {
  padding:3px 3px 3px 18px;
  background-color:#f0f0f0;
  color:#C20000;
  font:11px/normal "Lucida Grande",Helvetica,sans-serif;
}
.backtrace {
  color: #000;
  font-size: 12px;
}
a {
  color: #BE5C00;
}
.console {
  font-size: 12px;
  font-family: monospace;
  color: white;
  background-color: black;
  padding: 0.1em 0 0.2em 0;
  overflow:auto;
}
  </style>
</head>
<body>
<div class="rspec-report">

<div id="rspec-header">
  <div id="label">
    <h1>RSpec Error</h1>
  </div>
</div>

<div class="results">
  <div class="failure">
    <p class="message"><pre>${rspec_message}</pre></p>
    <p class="backtrace">${rspec_file_url}</p>
    <pre class="console"><code>${rspec_console}</code></pre>
  </div>
</div>
</div>
</body>
</html>
"""
    markup = Template(html_pattern)
    markup_out = markup.substitute(rspec_message=message, rspec_file_url=file_url, rspec_console=console)
    return markup_out

# Class

class BrowserPage(webkit.WebView):
    def __init__(self):
        webkit.WebView.__init__(self)

class RspecPlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)
        self.instances = {}

    def activate(self, window):
        self.instances[window] = RspecWindowHelper(self, window)

    def deactivate(self, window):
        self.instances[window].deactivate()
        del self.instances[window]

    def update_ui(self, window):
        self.instances[window].update_ui()

class RspecWindowHelper:
    handlers = {}
    mt = re.compile(r'(?P<protocol>^gedit:\/\/)(?P<file>.*?)\?line=(?P<line>.*?)$')

    def __init__(self, plugin, window):
        self.window = window
        self.plugin = plugin
        self.rspec_window = None
        self._browser = None
        self.client = gconf.client_get_default()
        self.add_menu()

    def deactivate(self):
        self._browser = None
        self.rspec_window = None
        self.window = None
        self.plugin = None

    def add_menu(self):
        actions = [
            ('RSpecTwo', gtk.STOCK_EDIT, _('Run all specs'), '<Super>r', _("Press Super + r to run all specs"), self.run_all_specs),
            ('RSpecOne', gtk.STOCK_EDIT, _('Run current spec'), '<Super>s', _("Press Super + s to run current spec"), self.run_current_spec)
        ]
        action_group = gtk.ActionGroup("RSpecActions")
        action_group.add_actions(actions, self.window)

        self.manager = self.window.get_ui_manager()
        self.manager.insert_action_group(action_group, -1)
        self.manager.add_ui_from_string(ui_str)

    # taken from snapopen plugin
    def get_filebrowser_root(self):
        base = u'/apps/gedit-2/plugins/filebrowser/on_load'
        client = gconf.client_get_default()
        client.add_dir(base, gconf.CLIENT_PRELOAD_NONE)
        path = os.path.join(base, u'virtual_root')
        val = client.get(path)

        if val is not None:
            base = u'/apps/gedit-2/plugins/filebrowser'
            client = gconf.client_get_default()
            client.add_dir(base, gconf.CLIENT_PRELOAD_NONE)
            path = os.path.join(base, u'filter_mode')
            fbfilter = client.get(path).get_string()

        return val.get_string()

    def run_all_specs(self, *args):
        uri = get_file_path(self.get_filebrowser_root())
        spec_path = get_root_path(uri)
        os.system("spec %s -f h:%s 2>&1 | tee %s" % (spec_path, TMP_FILE, OUT_FILE))

        if self.rspec_window:
            self.rspec_window.resize(700,510)
            self.rspec_window.show()
            self.rspec_window.grab_focus()
        else:
            self._browser = BrowserPage()
            self._gtk_4_browser = gtk.ScrolledWindow()
            self._browser.connect('navigation-requested', self.on_navigation_request)
            self.rspec_window = gtk.Window()
            self.rspec_window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
            self.rspec_window.resize(700,510)
            self.rspec_window.connect('delete_event', self.on_rspec_close)
            self.rspec_window.set_destroy_with_parent(True)
            self._gtk_4_browser.add(self._browser)
            self.rspec_window.add(self._gtk_4_browser)
            self.rspec_window.show_all()

        html_str = ''
        if os.path.isfile(TMP_FILE):
            f = open(TMP_FILE)
            for l in f.readlines():
                html_str += get_line(l)
            os.unlink(TMP_FILE)
            title = "All Specs"
        else:
            html_str = error_extract()
            title = "RSpec Error"

        self.rspec_window.set_title(title)
        self._browser.load_string(html_str, "text/html", "utf-8", "")

    def run_current_spec(self, *args):
        doc = self.window.get_active_document()
        str_uri = doc.get_uri()
        uri = gnomevfs.URI(str_uri)
        spec_path = get_spec(uri.path)
        os.system("spec %s -f h:%s 2>&1 | tee %s" % (spec_path, TMP_FILE, OUT_FILE))

        if self.rspec_window:
            self.rspec_window.resize(700,510)
            self.rspec_window.show()
            self.rspec_window.grab_focus()
        else:
            self._browser = BrowserPage()
            self._gtk_4_browser = gtk.ScrolledWindow()
            self._browser.connect('navigation-requested', self.on_navigation_request)
            self.rspec_window = gtk.Window()
            self.rspec_window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
            self.rspec_window.resize(700,510)
            self.rspec_window.connect('delete_event', self.on_rspec_close)
            self.rspec_window.set_destroy_with_parent(True)
            self._gtk_4_browser.add(self._browser)
            self.rspec_window.add(self._gtk_4_browser)
            self.rspec_window.show_all()

        html_str = ''
        if os.path.isfile(TMP_FILE):
            f = open(TMP_FILE)
            title = "Current Spec"
            for l in f.readlines():
                html_str += get_line(l)
                _title = get_title(l)
                if _title is not None:
                    title = "Spec to %s" % (_title)
            os.unlink(TMP_FILE)
        else:
            html_str = error_extract()
            title = "RSpec Error"

        self.rspec_window.set_title(title)
        self._browser.load_string(html_str, "text/html", "utf-8", "")

    def on_rspec_close(self, *args):
        self.rspec_window.hide()
        return True

    def on_navigation_request(self, page, frame, request):
        file_uri = None
        uri = request.get_uri()
        gp =  self.mt.search(uri)
        if gp:
            file_uri = 'file:///%s' % gp.group('file')
            line_number = gp.group('line')
            if file_uri:
                # Test if document is not already open
                for doc in self.window.get_documents():
                    if doc.get_uri() == file_uri:
                        tab = gedit.tab_get_from_document(doc)
                        view = tab.get_view()
                        self.window.set_active_tab(tab)
                        doc.goto_line(int(line_number))
                        view.scroll_to_cursor()
                        self.rspec_window.hide()
                        return 1
                # Document isn't open, create a new tab from uri
                self.window.create_tab_from_uri(file_uri,
                            gedit.encoding_get_current(),
                            int(line_number), False, True)
        else:
            print "(%s) not found" % file_uri
        self.rspec_window.hide()
        return 1

    def update(self, text=None):
        pass

    def update_ui(self):
        pass

    def set_data(self, name, value):
        self.window.get_active_tab().get_view().set_data(name, value)

    def get_data(self, name):
        return self.window.get_active_tab().get_view().get_data(name)
