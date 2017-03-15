<?php
/**
 *
 * Tool to clean csv and json files for usage in rdf
 * Immanuel Pelzer, 2016
 *
 * This file: Actual routes
 *
 */

$app->get('/', function () {
    $message = "";
    $server = $_SERVER['SERVER_NAME'];
    $output = <<<EOT
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">

    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>Housekeeper</title>
    </head>

    <body style="text-align:left;">
       <img src="./Noun_Project_Suche.png" alt="Cleanup" height="100" width="100">
        <br>
         <p>$message</p>
         
         <div style="text-align:left;">
         Usage: 
         <br><br>
         <b>Post JSON or CSV files to http://$server/clean with these parameters:</b>
         <br>?delete=column1,column2 // These columns will be deleted
         <br>&skip=column1,column2 // These columns will be skipped (not cleaned)
         <br>&output=csv // or json; defaults to json
         <br><br> Whitespaces in any of these parameters will be ignored. 
         <br><br>
         <i>Example: http://$server/clean?delete=column1,column2&skip=column1,column2&output=json </i>
         
         
         </div>
    </body>

    </html>
EOT;
    return $output;
});

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

$app->post('/clean', function (Request $request) {
    // settings
    $output_type = isset($_GET["outputType"]) ? $_GET["outputType"] : "csv"; // default to  csv

    // delete and skip parameters
    $delete = arrayify_or_null($_GET["delete"]);
    $skip = arrayify_or_null($_GET["skip"]);
    $willBeURI = arrayify_or_null($_GET["slugify"]);
    $htmlEntities = arrayify_or_null($_GET["htmlEntities"]);

    $options =  array(
        'delete' => $delete,
        'skip' => $skip,
        'slugify' => $willBeURI,
        'htmlEntities' => $htmlEntities,
        'extractUrls' => false
    );

    if ($skip == null) $skip = [];
    array_push($skip, "urls");

    // Convert to Associative Arrays
    $data = "";
    if (0 === strpos($request->headers->get('Content-Type'), 'application/json')) { // JSON
        $data = json_decode($request->getContent(), true);
    } elseif (0 === strpos($request->headers->get('Content-Type'), 'text/csv')) { // CSV
        $file = 'temp.csv';
        file_put_contents($file, $request->getContent());
        $array = $fields = array();
        $i = 0;
        $handle = @fopen($file, "r");
        if ($handle) {
            global $DELIMITER;
            while (($row = fgetcsv($handle, 4096, $DELIMITER, $enclosure = '"')) !== false) {
                if (empty($fields)) {
                    $fields = $row;
                    continue;
                }
                foreach ($row as $k => $value) {
                    $array[$i][$fields[$k]] = $value;
                }
                $i++;
            }
            if (!feof($handle)) {
                echo "Error: unexpected fgets() fail\n";
            }
            fclose($handle);
        }
        $data = $array;
    } else {
        return new Response('Data type not supported. Please use application/json or text/csv Content-Type.', 400);
    }

    /// Do the cleaning
    clean_array($data, $options);

    /// Return data to client
    if ($output_type == "csv") {
        $csvFileName = 'cleaned-data.csv';
        write_csv($csvFileName, $data);
        send_file_to_client_and_die($csvFileName);
        return new Response();
    } elseif ($output_type == "rdf") {
        if (!function_exists('str_putcsv')) {
            function str_putcsv($input, $delimiter = ',', $enclosure = '"')
            {
                $fp = fopen('php://temp', 'r+');
                fputcsv($fp, $input, $delimiter, $enclosure);
                rewind($fp);
                $data = fread($fp, 1048576);
                fclose($fp);
                return rtrim($data, "\n");
            }
        }

        $csvString = '';
        // Put header
        $csvString .= str_putcsv(array_keys($data[0])) . "\n";
        // Put content
        foreach ($data as $fields) {
            $csvString .= str_putcsv($fields) . "\n";
        }
        //return $csvString;
        //return $csvString;
        $data = curlRDFService("http://138.68.111.239/rdf/", $csvString);
        return new Response($data, 200, array(
            "Content-Type" => 'application/rdf+xml'
        ));

    } else { // Default to json
        $data = json_encode($data, JSON_UNESCAPED_UNICODE);
        return new Response($data, 200, array(
            "Content-Type" => 'application/json'
        ));
    }


    //return new Response('Success.');//
});


?>