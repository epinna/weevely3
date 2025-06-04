<%
overwrite_bool = 'true' if overwrite else 'false'
%>
$f='set_time_limit'&&is_callable($f)&&$f(0);
$f='ini_set'&&is_callable($f)&&$f('max_execution_time', 0);
$r=dirname(Phar::running(false)).'/';
$n='${ rtar }';
try {
    $a = new PharData($n);

% if decompress:

if(!file_exists($n) || !is_readable($n)) {
    print("Skipping file '$n', check existance and permission");
} else {
    $o = '${ rfiles[0] if rfiles and rfiles[0] else '.' }';
    $a->extractTo($o, null, ${ overwrite_bool });
}

% else:

if(file_exists($n) || !${ overwrite_bool }) {
    print("File '$n' already exists, skipping compressing");
} else {
    $b = dirname($n);

    function add($a, $b, $f) {
        $p = preg_replace("#^$b/#", '', $f);
        if (is_dir($f)) {
            $a->addEmptyDir($p);
            foreach(glob("$f/*") as $file) {
                add($a, $b, $file);
            }
        } else {
            $a->addFile($f, $p);
        }
    }

    % for f in rfiles:
    add($a, $b, '${ f }');
    % endfor
}

## Since makeTar does not complain for missing $n, just double
## check the existance of the zipped file and print generic error message
if(!file_exists($n)) {
    print("File '$n' not created, check existance and permission");
}

% endif

}catch(Exception $e){
    print("Skipping file '$n', check existance and permission");
}
