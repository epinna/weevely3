$opts = array(
  'http'=>array(
    'method'=>'${ request if not data else 'POST' }',
% if header or cookie or user_agent or data:
    'header' => array(
% endif
% for h in header:
        '${h}',
% endfor
% if cookie:
            'Cookie: ${ ' '.join(cookie) }',
% endif
% if user_agent:
            'User-Agent: ${ user_agent }',
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
print(file_get_contents('${url}', false, $ctx));
