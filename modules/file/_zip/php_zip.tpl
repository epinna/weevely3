<%include file="EasyZip.class.php"/>

$f='set_time_limit'&&is_callable($f)&&$f(0);
$f='ini_set'&&is_callable($f)&&$f('max_execution_time', 0);
$a = new zip;

$z = '${ rzip }';

$fs=array (
% for f in rfiles:
        '${ f }',
% endfor
);

## Here decompress
% if decompress:

if(!file_exists($z) || !is_readable($z)) {
    print("Skipping file '$z', check existance and permission");
}
else {
        $a->extractZip($z, '${ rfiles[0] if rfiles and rfiles[0] else '.' }');
}

## Here compress
% else:

if(file_exists($z)) {
    print("File $z already exists, skipping compressing");
}
else {
    $a->makeZip($fs, $z);
}

% endif
