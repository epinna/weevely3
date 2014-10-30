<%include file="EasyTar.class.php"/>

set_time_limit(0);
ini_set('max_execution_time', 0);
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
