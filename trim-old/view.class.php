<?php

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
