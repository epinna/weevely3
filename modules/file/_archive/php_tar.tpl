<%include file="EasyTar.class.php"/>

$f='set_time_limit'&&is_callable($f)&&$f(0);
$f='ini_set'&&is_callable($f)&&$f('max_execution_time', 0);
$a = new tar;
% if action == 'create':
$a->makeTar(
    array(
% for f in rfiles:
        '${ f }',
% endfor
    ),'${ rpath }');
% elif action == 'extract':
$a->extractTar('${ rpath }', '${ rfiles[0] }');
% endif
