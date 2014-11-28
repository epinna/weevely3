if(class_exists('HttpRequest')) {
    $r = new HttpRequest('${ url }', HttpRequest::METH_${ request if not data else 'POST' });

    $r->setOptions(array('connecttimeout'=>${ connect_timeout }));

    % if header or cookie or user_agent or data:
    $r->addHeaders(
        array(
    % for h in header:
            '${ h.split(':')[0] }' => '${ h.split(':')[1].lstrip() }',
    % endfor
    % if user_agent:
            'User-Agent'=>'${ user_agent }',
    % endif
    % if cookie:
              'Cookie'=>'${ cookie }',
    % endif
        )
    );
    % endif

    % if data:
    $r->addRawPostData('${ ''.join(data) }');
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
