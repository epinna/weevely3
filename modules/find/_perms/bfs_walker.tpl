function src($path, $search, $stop, $ftype, $perms, $no_recurs) {
	
	if (substr($path, -1) !== DIRECTORY_SEPARATOR)
		$path .= DIRECTORY_SEPARATOR;

	$queue = array($path => 1);
	$done  = array();
	$index = 0;
	while(!empty($queue)) {
		/* get one element from the queue */
		foreach($queue as $path => $unused) {
			unset($queue[$path]);
			$done[$path] = null;
			break;
		}
		unset($unused);

		$dh = @opendir($path);
		if (!$dh) continue;
		while(($filename = readdir($dh)) !== false) {
			/* dont recurse back up levels */
			if ($filename == '.' || $filename == '..')
				continue;

			/* check if the filename matches the search term */
			if (
				(!$search||preg_match("/$search/",$filename))&&
				(!strstr($perms,"w")||is_writable($filename))&&
                                (!strstr($perms,"x")||is_executable($filename))&&
                                (!strstr($perms,"r")||is_readable($filename))&&
                                (!strstr($ftype,"f")||is_file($filename))&&
                                (!strstr($ftype,"d")||is_dir($filename))
			) {
				echo "$path$filename" . PHP_EOL;
				if ($stop)
					break 2;
			}

			/* get the full path */
			$filename = $path . $filename;

			/* resolve symlinks to their real path */
			if (is_link($filename))
				$filename = realpath($filename);

			/* queue directories for later search */
			if (is_dir($filename)) {
				/* ensure the path has a trailing slash */
				if (substr($filename, -1) !== DIRECTORY_SEPARATOR)
					$filename .= DIRECTORY_SEPARATOR;

				/* check if we have already queued this path, or have done it */
				if ($no_recurs || array_key_exists($filename, $queue) || array_key_exists($filename, $done))
					continue;

				/* queue the file */
				$queue[$filename] = null;
			}
		}
		closedir($dh);
	}
}

src('${rpath}', '${ name_regex if name_regex else '' }', ${quit}, '${ ftype if ftype == 'd' or ftype == 'f' else '' }','${ '%s%s%s' % (('w' if writable else ''), ('r' if readable else ''), ('x' if executable else '') ) }', ${no_recursion});
