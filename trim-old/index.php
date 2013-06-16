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

define("DATABASE", "sqlite:" . $_SERVER["NFSN_SITE_ROOT"] . "protected/mappings.sqlite");

require_once("view.class.php");

$path = explode("?", $_SERVER["REQUEST_URI"], 2);
$path = substr($path[0], 1);

$view = new View();

switch($path) {
    case '':
        $view->set_template("index.php");
        break;
    default:
        $view->internal_code = $path;
        $db = new PDO(DATABASE);
        $stmt = $db->prepare("SELECT trim_code, url FROM trim_link WHERE internal_code = ?");
        $stmt->execute(array($path));
        $rows = $stmt->fetchAll();
        $stmt->closeCursor();
        if(count($rows) == 0) {
            header("HTTP/1.0 404 Not Found");
            $view->set_template("404.php");
        } elseif(count($rows) == 1) {
            $row = $rows[0];
            header("X-Trim-Code: " . $row[0]);
            header("Location: " . $row[1], true, 301);
            die();
        } else {
            header("HTTP/1.0 300 Multiple Choice");
            $view->rows = $rows;
            $view->set_template("multiple_codes.php");
        }
}

header("Content-Type: application/xhtml+xml; charset=UTF-8");
$view->render();
