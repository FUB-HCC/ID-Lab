<?php

/**
 *
 * Tool to clean csv and json files for usage in rdf
 * Immanuel Pelzer, 2016
 *
 * This file: Modules to clean the files and all helper code
 *
 */


// CODE


// Get all Dirs
function rmdir_recursive($dir)
{
    foreach (scandir($dir) as $file) {
        if ('.' === $file || '..' === $file) continue;
        if (is_dir("$dir/$file")) rmdir_recursive("$dir/$file");
        else unlink("$dir/$file");
    }

    rmdir($dir);
}

// Make comma seperated string an array or null
function arrayify_or_null($string)
{
    $return = null;
    if (isset($string)) {
        if ((strpos($string, ',') !== FALSE)) {
            $return = explode(",", str_replace(' ', '', $string));
        } else {
            $return = [$string];
        }
    }
    return $return;
}

// get all urls from string 
// http://stackoverflow.com/questions/910912/extract-urls-from-text-in-php
function getUrls($string)
{
    preg_match_all('#\bhttps?://[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|/))#', $string, $matches);
    return ($matches[0]);
}

// Check if String $hackstack starts with $needle
function startsWith($haystack, $needle)
{
    $length = strlen($needle);
    return (substr($haystack, 0, $length) === $needle);
}

// Check if String $hackstack ends with $needle
function endsWith($haystack, $needle)
{
    $length = strlen($needle);
    if ($length == 0) {
        return true;
    }

    return (substr($haystack, -$length) === $needle);
}

// Modules

// Clean for xml
// http://stackoverflow.com/questions/12229572/php-generated-xml-shows-invalid-char-value-27-message
function module_utf8_for_xml($string)
{
    return preg_replace('/[^\x{0009}\x{000a}\x{000d}\x{0020}-\x{D7FF}\x{E000}-\x{FFFD}]+/u', ' ', $string);
}

// Apply htmlspecialchars
function module_htmlspecialchars($content, $key, $options)
{
    return htmlspecialchars($content);
}

// Replace &
function module_replaceAmpersandsAndDohtmlspecialchars($content, $key, $options)
{
    $placeholder = "PLACEHOLDER-1u239ssss01-NOONESHOULDHAVETHISINTHEIRSTUFF";
    $wanted = "&#38;";
    $html_amph = "&amp;";
    $nonBreakingSpace = "&nbsp;";

    $content = str_replace($wanted, $placeholder, $content); // fine already
    $content = str_replace($html_amph, $placeholder, $content); // html amph
    $content = str_replace($nonBreakingSpace, " ", $content); // non breaking space
    $content = str_replace("&", $placeholder, $content); // &

    // Do HTML Entities or only html special chars
    if (isset($options['htmlEntities']) && in_array($key, $options['htmlEntities'])) {
        $content = htmlentities($content);
    } else {
        $content = htmlspecialchars($content); // htmlentities needs to be done here
    }

    $content = str_replace($placeholder, $wanted, $content); // replace with wanted
    return $content;
}

// Remove HTML
function module_removeHTML($content,  $key, $options)
{
    // Repair HTML first
    $tidy = new Tidy();


    // Usage http://php.net/manual/en/tidy.examples.basic.php
    // Possible settings http://tidy.sourceforge.net/docs/quickref.html
    $settings = array('show-body-only' => true,
        'wrap' => 0
    );

    $tidy->parseString($content, $settings, 'utf8');
    $tidy->cleanRepair();

    $content = $tidy;


    // Now delete it
    if (is_array($content)) {
        foreach ($content as $key => $value) {
            $content[$key] = strip_tags($value);
        }
    } else {
        $content = strip_tags($content);
    }
    return $content;
}

// Remove /n
function module_removeLineBreaks($content, $key, $options)
{
    return str_replace(array("\r\n", "\r", "\n"), ' ', $content);
}

// Helper Functions

// http://stackoverflow.com/a/10360316/2596452
function utf8_uri_encode($utf8_string, $length = 0)
{
    $unicode = '';
    $values = array();
    $num_octets = 1;
    $unicode_length = 0;

    $string_length = strlen($utf8_string);
    for ($i = 0; $i < $string_length; $i++) {

        $value = ord($utf8_string[$i]);

        if ($value < 128) {
            if ($length && ($unicode_length >= $length))
                break;
            $unicode .= chr($value);
            $unicode_length++;
        } else {
            if (count($values) == 0) $num_octets = ($value < 224) ? 2 : 3;

            $values[] = $value;

            if ($length && ($unicode_length + ($num_octets * 3)) > $length)
                break;
            if (count($values) == $num_octets) {
                if ($num_octets == 3) {
                    $unicode .= '%' . dechex($values[0]) . '%' . dechex($values[1]) . '%' . dechex($values[2]);
                    $unicode_length += 9;
                } else {
                    $unicode .= '%' . dechex($values[0]) . '%' . dechex($values[1]);
                    $unicode_length += 6;
                }

                $values = array();
                $num_octets = 1;
            }
        }
    }

    return $unicode;
}

//taken from wordpress
function seems_utf8($str)
{
    $length = strlen($str);
    for ($i = 0; $i < $length; $i++) {
        $c = ord($str[$i]);
        if ($c < 0x80) $n = 0; # 0bbbbbbb
        elseif (($c & 0xE0) == 0xC0) $n = 1; # 110bbbbb
        elseif (($c & 0xF0) == 0xE0) $n = 2; # 1110bbbb
        elseif (($c & 0xF8) == 0xF0) $n = 3; # 11110bbb
        elseif (($c & 0xFC) == 0xF8) $n = 4; # 111110bb
        elseif (($c & 0xFE) == 0xFC) $n = 5; # 1111110b
        else return false; # Does not match any model
        for ($j = 0; $j < $n; $j++) { # n bytes matching 10bbbbbb follow ?
            if ((++$i == $length) || ((ord($str[$i]) & 0xC0) != 0x80))
                return false;
        }
    }
    return true;
}

//function sanitize_title_with_dashes taken from wordpress
function sanitize($title)
{
    $title = strip_tags($title);
    // Preserve escaped octets.
    $title = preg_replace('|%([a-fA-F0-9][a-fA-F0-9])|', '---$1---', $title);
    // Remove percent signs that are not part of an octet.
    $title = str_replace('%', '', $title);
    // Restore octets.
    $title = preg_replace('|---([a-fA-F0-9][a-fA-F0-9])---|', '%$1', $title);

    if (seems_utf8($title)) {
        if (function_exists('mb_strtolower')) {
            $title = mb_strtolower($title, 'UTF-8');
        }
        $title = utf8_uri_encode($title, 200);
    }

    $title = strtolower($title);
    $title = preg_replace('/&.+?;/', '', $title); // kill entities
    //$title = str_replace('.', '-', $title); // Preserve dot
    $title = preg_replace('/[^%a-z0-9#. _-]/', '', $title); // original: [^%a-z0-9 _-], now includes #.
    $title = preg_replace('/\s+/', '-', $title); // replaces any whitespace cahracter
    $title = preg_replace('|-+|', '-', $title);
    $title = trim($title, '-'); // Strips -

    return $title;
}

// URIs standard  RFC 3986
// http://php.net/manual/de/function.urlencode.php
function myUrlEncode($string) {
    $entities = array('%21', '%2A', '%27', '%28', '%29', '%3B', '%3A', '%40', '%26', '%3D', '%2B', '%24', '%2C', '%2F', '%3F', '%25', '%23', '%5B', '%5D');
    $replacements = array('!', '*', "'", "(", ")", ";", ":", "@", "&", "=", "+", "$", ",", "/", "?", "%", "#", "[", "]");
    return str_replace($entities, $replacements, urlencode($string));
}

// Send file from local system to client
function send_file_to_client_and_die($filename)
{
    if (file_exists($filename)) {
        header('Content-Description: File Transfer');
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . basename($filename) . '"');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($filename));
        ob_clean();
        flush();
        readfile($filename);
        exit;
    }
}


// Clean an associaive array using all modules defined in $MODULES
// Also do urls
function clean_array(&$data, $options)
{
    // Do cleanup
    function my_walk_recursive(array &$array, $path = null, $options)
    {
        global $MODULES, $PLUGINS;
        foreach ($array as $k => &$v) {
            if (!is_array($v)) {
                // check for urls column
                if ($options["extractUrls"]) {
                    if (!array_key_exists("urls", $array)) {
                        $array["urls"] = "";
                    }
                }

                // delete
                if ($options["delete"] != null && in_array($k, $options["delete"])) { // check if row needs deleting
                    unset($array[$k]);
                } else {
                    if (!isset($options["skip"]) || !in_array($k, $options["skip"])) { // only do if not skippig

                        // first get all urls
                        if ($options["extractUrls"]) {
                            $urls = getUrls($v);
                            if (!empty($urls)) {
                                foreach ($urls as $url) {
                                    $array["urls"] = $array["urls"] . " " . $url;
                                }
                            }
                        }

                        // DO MODULES
                        foreach ($MODULES as $mod) {
                            /*echo "old: " .  $array[$k];
                            echo "new: " . $mod($v);*/

                            $array[$k] = $mod($v, $k, $options);
                            /*if ( strpos($v, 'Brighton') !== false) {
                                echo "after: " . $array[$k]. "\n\n\n";
                            }*/
                        }

                        // DO PLUGINS
                        foreach ($PLUGINS as $plugin) {
                            $array[$k] = $plugin($v, $k);
                        }

                        // Clean uris
                        if ($options["slugify"] != null && in_array($k, $options["slugify"])) {
                            // URL-Kodierung nach RFC 3986
                            $array[$k] = sanitize($v);
                        }
                    }
                }

            } else {
                my_walk_recursive($v, $path . '/' . $k, $options);
            }
        }
    }

    my_walk_recursive($data, null, $options);

}

// write data to a csv file to disc
function write_csv($csvFileName, $data)
{
    $fp = fopen($csvFileName, 'w');
    $firstLineKeys = false;
    foreach ($data as $row) {
        if (empty($firstLineKeys)) {
            $firstLineKeys = array_keys($row);
            fputcsv($fp, $firstLineKeys);
            $firstLineKeys = array_flip($firstLineKeys);
        }
        fputcsv($fp, $row);
    }
    fclose($fp);
    // send to client
}

// send data to server and return result
function curlRDFService($target_url, $content)
{
    $post = array('download' => 0, 'input' => $content);

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $target_url);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $result = curl_exec($ch);
    curl_close($ch);
    return $result;
}


// NOT USED


if ($_FILES["zip_file"]["name"] && false) { //please don't judge me
    $filename = $_FILES["zip_file"]["name"];
    $source = $_FILES["zip_file"]["tmp_name"];
    $type = $_FILES["zip_file"]["type"];

    $name = explode(".", $filename);
    $accepted_types = array('application/zip', 'application/x-zip-compressed', 'multipart/x-zip', 'application/x-compressed');
    foreach ($accepted_types as $mime_type) {
        if ($mime_type == $type) {
            $okay = true;
            break;
        }
    }

    $continue = strtolower($name[1]) == 'zip' ? true : false;
    if (!$continue) {
        $message = "The file you are trying to upload is not a .zip file. Please try again.";
    }

    /* PHP current path */
    $path = dirname(__FILE__) . '/';  // absolute path to the directory where zipper.php is in
    $filenoext = basename($filename, '.zip');  // absolute path to the directory where zipper.php is in (lowercase)
    $filenoext = basename($filenoext, '.ZIP');  // absolute path to the directory where zipper.php is in (when uppercase)

    $targetdir = $path . $filenoext; // target directory
    $targetzip = $path . $filename; // target zip file

    if (is_dir($targetdir)) rmdir_recursive($targetdir);


    mkdir($targetdir, 0777);


    // READING
    if (move_uploaded_file($source, $targetzip)) {
        $zip = new ZipArchive();
        $x = $zip->open($targetzip);  // open the zip file to extract
        if ($x === true) {
            $zip->extractTo($targetdir); // place in the directory with same name
            $zip->close();
            unlink($targetzip);

            // get all files in archive
            $path = $targetdir;
            $files = glob($targetdir . '/*.{csv,CSV}', GLOB_BRACE);

            // go threw all files
            foreach ($files as &$file) {
                $reading = fopen($file, 'r');
                $writing = fopen($file . '.tmp', 'w');
                $replaced = false;

                $row = 1;

                while (($data = fgetcsv($reading, 100000, $DELIMITER)) !== FALSE) {
                    $num = count($data);
                    $row++;
                    $newData = [];
                    for ($c = 0; $c < $num; $c++) {
                        //echo "old: " . $data[$c] . "<br>";
                        $newData[$c] = $data[$c];

                        foreach ($MODULES as $mod) {   /// MAGIC
                            $newData[$c] = $mod($newData[$c]);
                        }
                    }
                    fputcsv($writing, $newData, $DELIMITER);
                }

                fclose($reading);
                fclose($writing);
                // override old file
                rename($file . '.tmp', $file);
            }
        }

        /// ZIP FILES AND REMOVE FILES

        // Get real path for our folder
        $rootPath = realpath($targetdir);

        // Initialize archive object
        $zip = new ZipArchive();
        $zip->open('cleaned-files.zip', ZipArchive::CREATE | ZipArchive::OVERWRITE);

        // Create recursive directory iterator
        /** @var SplFileInfo[] $files */
        $files = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($rootPath),
            RecursiveIteratorIterator::LEAVES_ONLY
        );

        foreach ($files as $name => $file) {
            // Skip directories (they would be added automatically)
            if (!$file->isDir()) {
                // Get real and relative path for current file
                $filePath = $file->getRealPath();
                $relativePath = substr($filePath, strlen($rootPath) + 1);

                // Add current file to archive
                $zip->addFile($filePath, $relativePath);
            }
        }

        // Zip archive will be created only after closing object
        $zip->close();

        // Delete all files from "delete list"
        $dir = $targetdir;
        $it = new RecursiveDirectoryIterator($dir, RecursiveDirectoryIterator::SKIP_DOTS);
        $files = new RecursiveIteratorIterator($it,
            RecursiveIteratorIterator::CHILD_FIRST);
        foreach ($files as $file) {
            if ($file->isDir()) {
                rmdir($file->getRealPath());
            } else {
                unlink($file->getRealPath());
            }
        }
        rmdir($dir);

        $message = "Your .csv files were cleaned.";


        // Send file to client
        send_file_to_client_and_die("cleaned-files.zip");

    } else {
        $message = "There was a problem with the upload. Please try again.";
    }
}

// not used
/*function strip_tags_content($text, $tags = '', $invert = FALSE) {
    preg_match_all('/<(.+?)[\s]*\/?[\s]*>/si', trim($tags), $tags);
    $tags = array_unique($tags[1]);

    if(is_array($tags) AND count($tags) > 0) {
        if($invert == FALSE) {
            return preg_replace('@<(?!(?:'. implode('|', $tags) .')\b)(\w+)\b.*?>.*?</\1>@si', '', $text);
        }
        else {
            return preg_replace('@<('. implode('|', $tags) .')\b.*?>.*?</\1>@si', '', $text);
        }
    }
    elseif($invert == FALSE) {
        return preg_replace('@<(\w+)\b.*?>.*?</\1>@si', '', $text);
    }
    return $text;
}*/

?>