<%include file="EasyGzip.class.php"/>

$f='set_time_limit'&&is_callable($f)&&$f(0);
$f='ini_set'&&is_callable($f)&&$f('max_execution_time', 0);
$a = new gzip;
% if action == 'create':
$a->makeGzip('${ rfiles[0] }','${ rpath }');
% elif action == 'extract':
$a->extractGzip('${ rpath }', '${ rfiles[0] }');
% endif
