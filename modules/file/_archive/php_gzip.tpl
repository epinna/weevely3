<%include file="EasyGzip.class.php"/>

set_time_limit(0);
ini_set('max_execution_time', 0);
$a = new gzip;
% if action == 'create':
$a->makeGzip('${ rfiles[0] }','${ rpath }');
% elif action == 'extract':
$a->extractGzip('${ rpath }', '${ rfiles[0] }');
% endif
