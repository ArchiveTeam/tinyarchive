<?php

# TinyArchive - A tiny web archive
# Copyright (C) 2013 David Triendl
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class View {

    protected $vars = array();
    protected $template;

    function __set($name, $value) {
        $this->vars[$name] = $value;
    }

    function &__get($name) {
        return $this->vars[$name];
    }

    function __isset($name) {
        return isset($this->vars[$name]);
    }

    function __unset($name) {
        unset($this->vars[$name]);
    }

    public function set_template($template) {
        $this->template = $template;
    }

    public function render() {
        $include_path = get_include_path();
        set_include_path('templates/');
        $this->run();
        set_include_path($include_path);
    }

    protected function run() {
        foreach($this->vars as $key => $value)
            $$key = $value;
        require $this->template;
    }

    public static function escape($data) {
        return htmlentities($data, ENT_QUOTES);
    }

}
