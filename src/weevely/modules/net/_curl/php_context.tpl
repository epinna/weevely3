$opts = array(
  'ssl' => array (
    'verify_peer'       => false,
    'verify_peer_name'  => false,
    'allow_self_signed' => true,
    'verify_depth'      => 0,
  ),
  'http'=>array(
    'follow_location' => false,
    'method'=>'${ request if not data else 'POST' }',
    'timeout'=>${ connect_timeout },
    'ignore_errors' => true,
% if header or cookie or user_agent or data:
    'header' => array(
% endif
% for h in header:
%   if not (data and (h.title().startswith('Content-Length: '))) and not (user_agent and h.title().startswith('User-Agent: ')):
        "${h}",
%   endif
% endfor
% if cookie:
            "Cookie: ${ cookie }",
% endif
% if user_agent:
            "User-Agent: ${ user_agent }",
% endif
% if header or cookie or user_agent or data:
    ),
% endif
% if data:
    'content' => "${ ''.join(data) }",
% endif
  )
);

$ctx=stream_context_create($opts);
% if current_vector == 'file_get_contents':
$r = file_get_contents("${url}", false, $ctx);
% elif current_vector == 'fopen_stream_get_contents':
$s = fopen("${url}", 'r', false, $ctx);
$r = '';
if($s) {
    $r = stream_get_contents($s);
    fclose($s);
}
% elif current_vector == 'fopen_fread':
$h = fopen("${url}", 'r', false, $ctx);
$r = '';
if($h) {
    while (!feof($h)) {
      $r .= fread($h, 8192);
    }
    fclose($h);
}
% endif

foreach($http_response_header as $v) {
    print("$v\r\n");
}
print("\r\n". $r);
