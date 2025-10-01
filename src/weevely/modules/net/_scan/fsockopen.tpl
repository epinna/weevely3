$addrs = array( "${ '", "'.join( ips ) }" );
$ports = array( ${ ', '.join( [ str(p) for p in prts ] ) } );

foreach($addrs as $a) {
    foreach($ports as $p) {
        $n="";$e="";
        if($fp = fsockopen($a, $p, $n, $e, $timeout=${ timeout })) {
            print("OPN $a:$p" . PHP_EOL);
            fclose($fp);
        }
        else {
            print("ERR $a:$p $e $n" . PHP_EOL);
        }
    }
}
