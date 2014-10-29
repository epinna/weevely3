$ch = curl_init();

curl_setopt($ch, CURLOPT_URL, '${url}');

curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "${ request if not data else 'POST' }");
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, ${ connect_timeout });

% if header or cookie or user_agent or data:
curl_setopt($ch, CURLOPT_HTTPHEADER, array(
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
  ));
% endif

% if data:
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, '${ ''.join(data) }');
% endif

print(curl_exec($ch));
