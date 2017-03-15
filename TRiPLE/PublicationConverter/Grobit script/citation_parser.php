#!/usr/bin/php -q
<?php
/*
	Text to TEI converter - using GROBID
	Pre-requisites: running GROBID server on http://0.0.0.0:8080/
*/

// SETTINGS
$bibtexLocation = './Stylesheets-dev/bin/teitobibtex';	// Location of teitobibtex, should be included
$filename = 'BWG-website-citations-Oct-2016-withid.csv'; // Which file to convert
$outFilenameBib = 'parsed.bib'; // Out filename
$requestURL = 'http://0.0.0.0:8080/processCitation'; // Grobid server location

// SETTINGS END

$outFilename = 'parsed.xml';
file_put_contents($outFilename, "\xEF\xBB\xBF".  ""); 
$f = fopen($filename, 'rb');
$o = fopen($outFilename, 'ab');


if (!$f || !$o) {
	exit('Error opening file: ' . $filename);
}

$requestMethod = 'POST';


function trimStrings($item) {
	return trim($item);
}

echo "<br>Grobid...<br>";

$firstLine = true;
$allIds = array();

while($line = fgets($f)) {
	$line = utf8_encode($line); // ensure encoding
	if ($firstLine) { // Make file a TEI file
		$firstLine = false;
		fwrite($o, '<?xml version="1.0" encoding="UTF-8"?>');
		fwrite($o, '<TEI xmlns="http://www.tei-c.org/ns/1.0">');
	}

	$data = explode("|", $line);
	$line = $data[1];
	array_push($allIds,$data[0]);
	// replace / with and
	$line = str_replace('/', " and ", $line);

	// send a request to the GROBID server

	$requestString = 'input=' . '&' . 'citations=' . $line;

	$ch = curl_init( $requestURL );
	curl_setopt( $ch, CURLOPT_POST, 1 );
	curl_setopt( $ch, CURLOPT_POSTFIELDS, $requestString );
	curl_setopt( $ch, CURLOPT_FOLLOWLOCATION, 1 );
	curl_setopt( $ch, CURLOPT_HEADER, 0 );
	curl_setopt( $ch, CURLOPT_RETURNTRANSFER, 1 );

	$response = curl_exec( $ch );

	// prepare the TEI data
	$strings = explode(PHP_EOL, $response);
	// trim the lines
	$trimmedStrings = array_map("trimStrings", $strings);
	$response = implode("", $trimmedStrings);

	// $response = str_replace(array("\n\r", "\n", "\r"), "", $response);
	$response = trim($response) . PHP_EOL;

	// output the original line and the parsed citation in TEI format
	//$csvLine = $line. '|' . $response;
	// write the TEI data
	fwrite($o, $response); // utf8_encode?
}
fwrite($o, '</TEI>'); // end of tei file
fclose($f);
fclose($o);


echo "Adding ids...<br>";

$dom=new DOMDocument();
$dom->load("$outFilename");

$root=$dom->documentElement; 
//echo $root->getElementsByTagName('biblStruct ')->textContent;

//$markers=$root->getElementsByTagName('biblStruct');

// Loop trough childNodes
foreach ($root->getElementsByTagName('biblStruct') as $index=>$bib) {
     $bib->setAttribute("id", str_replace('"', "", $allIds[$index])); //
}
$dom->saveXML();
$dom->save($outFilename); 




echo "Converting to Bibtex...<br>";
ini_set('memory_limit', '-1');
shell_exec($bibtexLocation . " " . $outFilename . " " . $outFilenameBib);
echo "Finished🎉<br>";

