<%include file="EasyBzip2.class.php"/>

$f='set_time_limit'&&is_callable($f)&&$f(0);
$f='ini_set'&&is_callable($f)&&$f('max_execution_time', 0);
$a = new bzip2;
% if action == 'create':
$a->makeBzip2('${ rfiles[0] }','${ rpath }');
% elif action == 'extract':
$a->extractBzip2('${ rpath }', '${ rfiles[0] }');
% endif
