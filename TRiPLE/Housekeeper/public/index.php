<?php
error_reporting(E_ERROR | E_PARSE);
// Silex app
require_once __DIR__.'/vendor/autoload.php';

/**
 * Tool to clean csv and json files for usage in rdf
 * Immanuel Pelzer, 2016
 */
include "modules.php";
include "plugins.php";

// SETTINGS
$DELIMITER = ","; // used in csv
$MODULES =  [module_removeHTML,module_replaceAmpersandsAndDohtmlspecialchars, module_removeLineBreaks, module_utf8_for_xml]; // all functions are applied on all fields
$PLUGINS = [plugin_makeBoolean(["active"])];
$DEBUG = false;


// Setup app
$app = new Silex\Application();
if ($DEBUG) $app['debug'] = true;

// Components
include "before.php";
include "routes.php";

$app->run();


?>
