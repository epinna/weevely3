<%include file="EasyBzip2.class.php"/>

$f='set_time_limit'&&is_callable($f)&&$f(0);
$f='ini_set'&&is_callable($f)&&$f('max_execution_time', 0);
$a = new bzip2;

$fs=array (
% for f in rpaths:
        '${ f }',
% endfor
);

foreach($fs as $f) {
    if(!file_exists($f) || !is_readable($f)) {
        print("Skipping file '$f', check existance and permission");
    }
    else {

## Here decompress
% if decompress:
    $ext = pathinfo($f, PATHINFO_EXTENSION);
    if(!preg_match('/t?bz2?$/', $ext)) {
        print("Unknown suffix, skipping decompressing");
    }
    else {
        $nf = substr($f, 0, -strlen($ext)-1);
        if(file_exists($nf)) {
            print("File '$nf' already exists, skipping decompressing");
        }
        else {
            $a->extractBzip2($f, $nf);
% if not keep:
            if(file_exists($nf)) unlink($f);
%endif
        }
    }
## Here compress
% else:

        if(file_exists($f.'.bz2')) {
            print("File '$f.bz2' already exists, skipping compressing");
        }
        else {
                $a->makeBzip2($f, $f.'.bz2');
% if not keep:
                if(file_exists($f.'.bz2')) unlink($f);
%endif
        }
% endif
    }
}
