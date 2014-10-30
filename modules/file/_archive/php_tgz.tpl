<%include file="EasyGzip.class.php"/>
<%include file="EasyTar.class.php"/>

$f='set_time_limit'&&is_callable($f)&&$f(0);
$f='ini_set'&&is_callable($f)&&$f('max_execution_time', 0);
$a = new gzip;
$t = new tar;
% if action == 'create':
$t->makeTar(
    array(
% for f in rfiles:
        '${ f }',
% endfor
    ),'${ rpath }_temp_tar');
$a->makeGzip('${ rpath }_temp_tar','${ rpath }');
% elif action == 'extract':
$a->extractGzip('${ rpath }', '${ rpath }_temp_tar');
$t->extractTar('${ rpath }_temp_tar', '${ rfiles[0] }');
% endif
unlink('${ rpath }_temp_tar');
