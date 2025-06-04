/**-------------------------------------------------
 | EasyBzip2.class V0.8 -  by Alban LOPEZ
 | Copyright (c) 2007 Alban LOPEZ
 | Email bugs/suggestions to alban.lopez+eazybzip2@gmail.com
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
class bzip2
{
/**
// You can use this class like that.
$test = new bzip2;
$test->makeBzip2('./','./toto.bzip2');
var_export($test->infosBzip2('./toto.bzip2'));
$test->extractBzip2('./toto.bzip2', './new/');
**/
	function makeBzip2($src, $dest=false)
	{
        // Adjusted to use $src just as file path instead of data source
		$Bzip2 = bzcompress(file_get_contents ($src), 6);
		if (empty($dest)) return $Bzip2;
		elseif (file_put_contents($dest, $Bzip2)) return $dest;
		return false;
	}
	function infosBzip2 ($src, $data=true)
	{
		$data = $this->extractBzip2 ($src);
		$content = array(
			'UnCompSize'=>strlen($data),
			'Size'=>filesize($src),
			'Ratio'=>strlen($data) ? round(100 - filesize($src) / strlen($data)*100, 1) : false,);
		if ($data) $content['Data'] = $data;
		return $content;
	}
	function extractBzip2($src, $dest=false)
	{
		$bz = bzopen($src, "r");
		$data = '';
		while (!feof($bz))
			$data .= bzread($bz, 1024*1024);
		bzclose($bz);
		if (empty($dest)) return $data;
		elseif (file_put_contents($dest, $data)) return $dest;
		return false;
	}
}
