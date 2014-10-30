<%include file="EasyZip.class.php"/>

set_time_limit(0);
ini_set('max_execution_time', 0);
$a = new zip;
% if action == 'create':
$a->makeZip('${ rfiles[0] }','${ rpath }');
% elif action == 'extract':
$a->extractZip('${ rpath }', '${ rfiles[0] }');
% endif
