<?php

define('DATABASE', $_SERVER["NFSN_SITE_ROOT"] . "protected/mapping.db");

require_once("view.class.php");

$path = explode('?', $_SERVER["REQUEST_URI"], 2);
$path = substr($path[0], 1);

$view = new View();

switch($path) {
    case '':
        $view->set_template("index.php");
        break;
    default:
        $view->internal_code = $path;
        $dba = dba_open(DATABASE, "r", "db4");
        if($dba === FALSE) {
            die("Database error");
        }
        $data = dba_fetch($path, $dba);
        dba_close($dba);
        if($data === FALSE) {
            header('HTTP/1.0 404 Not Found');
            $view->set_template("unknown_mapping.php");
        } else {
            $data = explode("|", $data, 2);
            header("X-Trim-Code: " . $data[0]);
            if(count($data) == 1) {
                header('HTTP/1.0 404 Not Found');
                $view->code = $data[0];
                $view->set_template("unknown_code.php");
            } else {
                header("Location: " . $data[1], true, 301);
                die();
            }
        }
}

header("Content-Type: application/xhtml+xml; charset=UTF-8");
$view->render();
