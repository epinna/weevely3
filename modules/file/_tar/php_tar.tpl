<%include file="EasyTar.class.php"/>

$f='set_time_limit'&&is_callable($f)&&$f(0);
$f='ini_set'&&is_callable($f)&&$f('max_execution_time', 0);
$a = new tar;

$z = '${ rtar }';

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
        $a->extractTar($z, '${ rfiles[0] if rfiles and rfiles[0] else '.' }');
}

## Here compress
% else:

if(file_exists($z)) {
    print("File '$z' already exists, skipping compressing");
}
else {
    $a->makeTar($fs, $z);
}

## Since makeTar does not complain for missing $z, just double
## check the existance of the zipped file and print generic error message
if(!file_exists($z)) {
    print("File '$z' not created, check existance and permission");
}

% endif
