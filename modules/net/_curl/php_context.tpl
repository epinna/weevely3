$opts = array(
  'http'=>array(
    'method'=>'${ request if not data else 'POST' }',
    'timeout'=>${ connect_timeout },
% if header or cookie or user_agent or data:
    'header' => array(
% endif
% for h in header:
        '${h}',
% endfor
% if cookie:
            'Cookie: ${ cookie }',
% endif
% if user_agent:
            "User-Agent: ${ user_agent }",
% endif
% if data:
            'Content-Type: application/x-www-form-urlencoded',
            'Content-Length: ${ len(''.join(data)) }',
% endif
% if header or cookie or user_agent or data:
    ),
% endif
% if data:
    'content' => '${ ''.join(data) }',
% endif
  )
);

$ctx=stream_context_create($opts);
% if current_vector == 'file_get_contents':
print(file_get_contents('${url}', false, $ctx));
% elif current_vector == 'fopen_stream_get_contents':
$s = fopen('${url}', 'r', false, $ctx);
if($s) {
    print(stream_get_contents($s));
    fclose($s);
}
% elif current_vector == 'fopen_fread':
$h = fopen('${url}', 'r', false, $ctx);
if($h) {
    $c = '';
    while (!feof($h)) {
      $c .= fread($h, 8192);
    }
    fclose($h);
    print($c);
}
% endif
