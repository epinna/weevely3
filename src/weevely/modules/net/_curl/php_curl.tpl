$ch = curl_init();

curl_setopt($ch, CURLOPT_URL, "${url}");

curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "${ request if not data else 'POST' }");
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, ${ connect_timeout });
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);

% if header or cookie or user_agent or data:
curl_setopt($ch, CURLOPT_HTTPHEADER, array(
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
  ));
% endif

% if data:
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, "${ ''.join(data) }");
% endif

curl_setopt($ch, CURLOPT_HEADER, 1);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
$response = curl_exec($ch);
print($response);
