if(class_exists('HttpRequest')) {
    $r = new HttpRequest("${ url }", HttpRequest::METH_${ request if not data else 'POST' });

    $r->setOptions(array('connecttimeout'=>${ connect_timeout }));

    % if header or cookie or user_agent or data:
    $r->addHeaders(
        array(
    % for h in header:
    %   if not (data and (h.title().startswith('Content-Length: '))) and not (user_agent and h.title().startswith('User-Agent: ')):
            "${ h.split(':')[0] }" => "${ h.split(':')[1].lstrip() }",
    %   endif
    % endfor
    % if user_agent:
            'User-Agent'=>"${ user_agent }",
    % endif
    % if cookie:
              'Cookie'=>"${ cookie }",
    % endif
        )
    );
    % endif

    % if data:
    $r->addRawPostData("${ ''.join(data) }");
    % endif

    try {
        $r = $r->send();
    } catch (HttpException $ex) { }

    print("HTTP/" . $r->getHttpVersion() . " " . $r->getResponseCode() . " " . $r->getResponseStatus() . "\r\n");

    foreach($r->getHeaders() as $h => $v) {
        print("$h: $v\r\n");
    }
    print("\r\n" . $r->getBody());
}
