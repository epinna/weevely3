/**-------------------------------------------------
 | EasyZip.class V0.8 -  by Alban LOPEZ
 | Copyright (c) 2007 Alban LOPEZ
 | Email bugs/suggestions to alban.lopez+easyzip@gmail.com
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
// I remove every reference to realpath(), due I prefer to store files
// into the zip with the given relative path.
class zip
{
/**
// You can use this class like that.
$test = new zip;
$test->makeZip('./','./toto.zip');
var_export($test->infosZip('./toto.zip'));
$test->extractZip('./toto.zip', './new/');
**/
	function infosZip ($src, $data=true)
	{
		if (($zip = zip_open($src)))
		{
			while (($zip_entry = zip_read($zip)))
			{
				$path = zip_entry_name($zip_entry);
				if (zip_entry_open($zip, $zip_entry, "r"))
				{
					$content[$path] = array (
						'Ratio' => zip_entry_filesize($zip_entry) ? round(100-zip_entry_compressedsize($zip_entry) / zip_entry_filesize($zip_entry)*100, 1) : false,
						'Size' => zip_entry_compressedsize($zip_entry),
						'UnCompSize' => zip_entry_filesize($zip_entry));
					if ($data)
						$content[$path]['Data'] = zip_entry_read($zip_entry, zip_entry_filesize($zip_entry));
					zip_entry_close($zip_entry);
				}
				else
					$content[$path] = false;
			}
			zip_close($zip);
			return $content;
		}
		return false;
	}
	function extractZip ($src, $dest)
	{
		$zip = new ZipArchive;
		if ($zip->open($src)===true)
		{
			$zip->extractTo($dest);
			$zip->close();
			return true;
		}
		return false;
	}
	function makeZip ($src, $dest)
	{
		$zip = new ZipArchive;
		$src = is_array($src) ? $src : array($src);
		if ($zip->open($dest, ZipArchive::CREATE) === true)
		{
			foreach ($src as $item)
			{
				if (is_dir($item)) {
					$this->addZipItem($zip, dirname($item).'/', $item.'/');
                }
				elseif(is_file($item)) {
					$zip->addFile($item, $item);
                }
			}
			$zip->close();
			return true;
		}
		return false;
	}
	function addZipItem ($zip, $racine, $dir)
	{
		if (is_dir($dir))
		{
			$zip->addEmptyDir(str_replace($racine, '', $dir));
			$lst = scandir($dir);
			array_shift($lst);
			array_shift($lst);
			foreach ($lst as $item) {
				$this->addZipItem($zip, $racine, $dir.$item.(is_dir($dir.$item)?'/':''));
            }
		}
		elseif (is_file($dir)) {
			$zip->addFile($dir, str_replace($racine, '', $dir));
        }
	}
}
