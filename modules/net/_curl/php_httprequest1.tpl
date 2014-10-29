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
              'Cookie'=>'${ ' '.join(cookie) }',
    % endif
        )
    );
    % endif

    % if data:
    $r->addRawPostData('${ data }');
    % endif

    try {
        echo $r->send()->getBody();
    } catch (HttpException $ex) { }

}
