/**-------------------------------------------------
 | EasyGzip.class V0.8 -  by Alban LOPEZ
 | Copyright (c) 2007 Alban LOPEZ
 | Email bugs/suggestions to alban.lopez+easygzip@gmail.com
 +--------------------------------------------------
 | This file is part of EasyArchive.class V0.9.
 | EasyArchive is free software: you can redistribute it and/or modify
 | it under the terms of the GNU General Public License as published by
 | the Free Software Foundation, either version 3 of the License, or
 | (at your option) any later version.
 | EasyArchive is distributed in the hope that it will be useful,
 | but WITHOUT ANY WARRANTY; without even the implied warranty of
 | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 | See the GNU General Public License for more details on http://www.gnu.org/licenses/
 +--------------------------------------------------
 http://www.phpclasses.org/browse/package/4239.html **/
class gzip
{
/**
// You can use this class like that.
$test = new gzip;
$test->makeGzip('./','./toto.gzip');
var_export($test->infosGzip('./toto.gzip'));
$test->extractGzip('./toto.gzip', './new/');
**/
	function makeGzip($src, $dest=false)
	{
        // Adjusted to use $src just as file path instead of data source

		$Gzip = gzencode(file_get_contents ($src), 6);
		if (empty($dest)) return $Gzip;
		elseif (file_put_contents($dest, $Gzip)) return $dest;
		return false;
	}
	function infosGzip ($src, $data=true)
	{
		$data = $this->extractGzip ($src);
		$content = array(
			'UnCompSize'=>strlen($data),
			'Size'=>filesize($src),
			'Ratio'=>strlen($data) ? round(100 - filesize($src) / strlen($data)*100, 1) : false,);
		if ($data) $content['Data'] = $data;
		return $content;
	}
	function extractGzip ($src, $dest=false)
	{
		$zp = gzopen( $src, "r" );
		$data = '';
		while (!gzeof($zp))
			$data .= gzread($zp, 1024*1024);
		gzclose( $zp );
		if (empty($dest)) return $data;
		elseif (file_put_contents($dest, $data)) return $dest;
		return false;
	}
}
