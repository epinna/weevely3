<%include file="EasyBzip2.class.php"/>

set_time_limit(0);
ini_set('max_execution_time', 0);
$a = new bzip2;
% if action == 'create':
$a->makeBzip2('${ rfiles[0] }','${ rpath }');
% elif action == 'extract':
$a->extractBzip2('${ rpath }', '${ rfiles[0] }');
% endif
