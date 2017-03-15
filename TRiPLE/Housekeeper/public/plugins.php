<?php
/**
 * Created by PhpStorm.
 * User: immanuelpelzer
 * Date: 02.11.16
 * Time: 17:58
 *
 * Add Plugins here. All plugins have to use this pattern:
 * function($value, $column) use (...) {...}
 *
 */




/**
 * Makes a column (or columns) a boolean value
 *
 * "t" to true
 * "f" to false
 *
 * @param Array $columnsToMakeBoolean Array containing the column name as strings (or a string containing one column).
 * @return boolean Value as boolean (or original value if failed)
 */
function plugin_makeBoolean($columnsToMakeBoolean) { //
    if (!is_array($columnsToMakeBoolean)) $columnsToMakeBoolean = [$columnsToMakeBoolean];
    $plugin = function($value, $column) use ($columnsToMakeBoolean) {
        if (in_array($column,$columnsToMakeBoolean)) {
            if ($value == "f") {
                return false;
            } elseif ($value == "t") {
                return true;
            } else {
                return $value;
            }
        } else {
            return $value;
        }
    };
    return $plugin;
}

?>