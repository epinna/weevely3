<%include file="EasyZip.class.php"/>

$f='set_time_limit'&&is_callable($f)&&$f(0);
$f='ini_set'&&is_callable($f)&&$f('max_execution_time', 0);
$a = new zip;
% if action == 'create':
$a->makeZip('${ rpath }', '${ rfiles[0] }');
% elif action == 'extract':
$a->extractZip('${ rpath }', '${ rfiles[0] }');
% endif
