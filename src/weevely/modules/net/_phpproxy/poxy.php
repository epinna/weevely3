<?php

/*
   +-----------------+------------------------------------------------------------+
   |  Script         | PHProxy                                                    |
   |  Author         | Abdullah Arif                                              |
   |  Last Modified  | 5:27 PM 1/20/2007                                          |
   +-----------------+------------------------------------------------------------+
   |  This program is free software; you can redistribute it and/or               |
   |  modify it under the terms of the GNU General Public License                 |
   |  as published by the Free Software Foundation; either version 2              |
   |  of the License, or (at your option) any later version.                      |
   |                                                                              |
   |  This program is distributed in the hope that it will be useful,             |
   |  but WITHOUT ANY WARRANTY; without even the implied warranty of              |
   |  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |
   |  GNU General Public License for more details.                                |
   |                                                                              |
   |  You should have received a copy of the GNU General Public License           |
   |  along with this program; if not, write to the Free Software                 |
   |  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. |
   +------------------------------------------------------------------------------+
*/

error_reporting(E_ALL);

//
// CONFIGURABLE OPTIONS
//

$_config            = array
                    (
                        'url_var_name'             => 'q',
                        'flags_var_name'           => 'hl',
                        'get_form_name'            => '____pgfa',
                        'basic_auth_var_name'      => '____pbavn',
                        'max_file_size'            => -1,
                        'allow_hotlinking'         => 0,
                        'upon_hotlink'             => 1,
                        'compress_output'          => 0
                    );
$_flags             = array
                    (
                        'include_form'    => 1,
                        'remove_scripts'  => 1,
                        'accept_cookies'  => 1,
                        'show_images'     => 1,
                        'show_referer'    => 1,
                        'rotate13'        => 0,
                        'base64_encode'   => 1,
                        'strip_meta'      => 1,
                        'strip_title'     => 0,
                        'session_cookies' => 1
                    );
$_frozen_flags      = array
                    (
                        'include_form'    => 0,
                        'remove_scripts'  => 0,
                        'accept_cookies'  => 0,
                        'show_images'     => 0,
                        'show_referer'    => 0,
                        'rotate13'        => 0,
                        'base64_encode'   => 0,
                        'strip_meta'      => 0,
                        'strip_title'     => 0,
                        'session_cookies' => 0
                    );
$_labels            = array
                    (
                        'include_form'    => array('Include Form', 'Include mini URL-form on every page'),
                        'remove_scripts'  => array('Remove Scripts', 'Remove client-side scripting (i.e JavaScript)'),
                        'accept_cookies'  => array('Accept Cookies', 'Allow cookies to be stored'),
                        'show_images'     => array('Show Images', 'Show images on browsed pages'),
                        'show_referer'    => array('Show Referer', 'Show actual referring Website'),
                        'rotate13'        => array('Rotate13', 'Use ROT13 encoding on the address'),
                        'base64_encode'   => array('Base64', 'Use base64 encodng on the address'),
                        'strip_meta'      => array('Strip Meta', 'Strip meta information tags from pages'),
                        'strip_title'     => array('Strip Title', 'Strip page title'),
                        'session_cookies' => array('Session Cookies', 'Store cookies for this session only')
                    );

$_hosts             = array
                    (
                        '#^127\.|192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|localhost#i'
                    );
$_hotlink_domains   = array();
$_insert            = array();

//
// END CONFIGURABLE OPTIONS. The ride for you ends here. Close the file.
//

$_iflags            = '';
$_system            = array
                    (
                        'ssl'          => extension_loaded('openssl') && version_compare(PHP_VERSION, '4.3.0', '>='),
                        'uploads'      => ini_get('file_uploads'),
                        'gzip'         => extension_loaded('zlib') && !ini_get('zlib.output_compression'),
                        'stripslashes' => get_magic_quotes_gpc()
                    );
$_proxify           = array('text/html' => 1, 'application/xml+xhtml' => 1, 'application/xhtml+xml' => 1, 'text/css' => 1);
$_version           = '0.5b2';
$_http_host         = isset($_SERVER['HTTP_HOST']) ? $_SERVER['HTTP_HOST'] : (isset($_SERVER['SERVER_NAME']) ? $_SERVER['SERVER_NAME'] : 'localhost');
$_script_url        = 'http' . ((isset($_ENV['HTTPS']) && $_ENV['HTTPS'] == 'on') || $_SERVER['SERVER_PORT'] == 443 ? 's' : '') . '://' . $_http_host . ($_SERVER['SERVER_PORT'] != 80 && $_SERVER['SERVER_PORT'] != 443 ? ':' . $_SERVER['SERVER_PORT'] : '') . $_SERVER['PHP_SELF'];
$_script_base       = substr($_script_url, 0, strrpos($_script_url, '/')+1);
$_url               = '';
$_url_parts         = array();
$_base              = array();
$_socket            = null;
$_request_method    = $_SERVER['REQUEST_METHOD'];
$_request_headers   = '';
$_cookie            = '';
$_post_body         = '';
$_response_headers  = array();
$_response_keys     = array();
$_http_version      = '';
$_response_code     = 0;
$_content_type      = 'text/html';
$_content_length    = false;
$_content_disp      = '';
$_set_cookie        = array();
$_retry             = false;
$_quit              = false;
$_basic_auth_header = '';
$_basic_auth_realm  = '';
$_auth_creds        = array();
$_response_body     = '';

//
// FUNCTION DECLARATIONS
//

function show_report($data)
{
    ?>

    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
    <head>
        <title>PHProxy</title>
<style>
body, input
{
    font-family: "Bitstream Vera Sans", Arial, Helvetica, sans-serif;
    color: #44352C;
}

a
{
    color: #9B9C83;
    text-decoration:none;
    border-bottom: 1px orange dashed;
}

a:hover
{
    color: #0080FF;
}

#container
{
    border: 1px #9B9C83 solid;
    -moz-border-radius: 8px;
    margin: auto;
    padding: 5px;
    width: 700px;
}

#title
{
    color: #CC6633;
    margin: 0;
}

ul#navigation, ul#form
{
    list-style-type: none;
    padding: 0;
    margin: 0;
}

ul#navigation
{
    float: right;
}

ul#form
{
    clear: both;
}

ul#navigation li
{
    float: left;
    margin: 0;
    padding: 5px 0;
    border-top: 2px #BFAA9B solid;
}

ul#navigation li a
{
    font-weight: bold;
    color: #ffffff;
    background-color: #AA8E79;
    padding: 5px 15px;
    margin-left: 1px;
    text-decoration: none;
    border-bottom: 0 #ffffff solid;
}

ul#navigation li  a:hover
{
    color: #44352C;
}

ul#form li
{
    width: 700px;
}

#footer
{
    color: #9B9C83;
    font-size: small;
    text-align: right;
}

#address_bar
{
    border-top: 2px #BFAA9B solid;
    border-bottom: 3px #44352C solid;
    background-color: #AA8E79;
    text-align: center;
    padding: 5px 0;
    color: #ffffff;
}

#go
{
    background-color: #ffffff;
    font-weight: bold;
    color: #AA8E79;
    border: 0 #ffffff solid;
    padding: 2px 5px;
}

#address_box
{
    width: 500px;
}

.option
{
    padding: 2px 0;
    background-color: #EEEBEA;
}

.option label
{
    border-bottom: 2px #ffffff solid;
}

form
{
    margin: 0;
}

#error, #auth
{
    background-color: #BF6464;
    border-top: 1px solid #44352C;
    border-bottom: 1px solid #44352C;
    width: 700px;
    clear: both;
}

#auth
{
    background-color: #94C261;
}

#error p, #auth p, #auth form
{
    margin: 5px;
}
</style>
    </head>
    <body onload="document.getElementById('address_box').focus()">
        <div id="container">
            <h1 id="title">PHProxy</h1>
            <ul id="navigation">
                <li><a href="<?php echo $GLOBALS['_script_base'] ?>">URL Form</a></li>
                <li><a href="javascript:alert('cookie managment has not been implemented yet')">Manage Cookies</a></li>
            </ul>
            <?php

            switch ($data['category'])
            {
                case 'auth':
                ?>
                <div id="auth"><p>
                    <b>Enter your username and password for "<?php echo htmlspecialchars($data['realm']) ?>" on <?php echo $GLOBALS['_url_parts']['host'] ?></b>
                    <form method="post" action="">
                        <input type="hidden" name="<?php echo $GLOBALS['_config']['basic_auth_var_name'] ?>" value="<?php echo base64_encode($data['realm']) ?>" />
                        <label>Username <input type="text" name="username" value="" /></label> <label>Password <input type="password" name="password" value="" /></label> <input type="submit" value="Login" />
                    </form></p></div>
                    <?php
                    break;
                    case 'error':
                    echo '<div id="error"><p>';

                    switch ($data['group'])
                    {
                        case 'url':
                        echo '<b>URL Error (' . $data['error'] . ')</b>: ';
                        switch ($data['type'])
                        {
                            case 'internal':
                            $message = 'Failed to connect to the specified host. '
                            . 'Possible problems are that the server was not found, the connection timed out, or the connection refused by the host. '
                            . 'Try connecting again and check if the address is correct.';
                            break;
                            case 'external':
                            switch ($data['error'])
                            {
                                case 1:
                                $message = 'The URL you\'re attempting to access is blacklisted by this server. Please select another URL.';
                                break;
                                case 2:
                                $message = 'The URL you entered is malformed. Please check whether you entered the correct URL or not.';
                                break;
                            }
                            break;
                        }
                        break;
                        case 'resource':
                        echo '<b>Resource Error:</b> ';
                        switch ($data['type'])
                        {
                            case 'file_size':
                            $message = 'The file your are attempting to download is too large.<br />'
                            . 'Maxiumum permissible file size is <b>' . number_format($GLOBALS['_config']['max_file_size']/1048576, 2) . ' MB</b><br />'
                            . 'Requested file size is <b>' . number_format($GLOBALS['_content_length']/1048576, 2) . ' MB</b>';
                            break;
                            case 'hotlinking':
                            $message = 'It appears that you are trying to access a resource through this proxy from a remote Website.<br />'
                            . 'For security reasons, please use the form below to do so.';
                            break;
                        }
                        break;
                    }

                    echo 'An error has occured while trying to browse through the proxy. <br />' . $message . '</p></div>';
                    break;
                }
                ?>
                <form method="post" action="<?php echo $_SERVER['PHP_SELF'] ?>">
                    <ul id="form">
                        <li id="address_bar"><label>Web Address <input id="address_box" type="text" name="<?php echo $GLOBALS['_config']['url_var_name'] ?>" value="<?php echo isset($GLOBALS['_url']) ? htmlspecialchars($GLOBALS['_url']) : '' ?>" onfocus="this.select()" /></label> <input id="go" type="submit" value="Go" /></li>
                        <?php

                        foreach ($GLOBALS['_flags'] as $flag_name => $flag_value)
                        {
                            if (!$GLOBALS['_frozen_flags'][$flag_name])
                            {
                                echo '<li class="option"><label><input type="checkbox" name="' . $GLOBALS['_config']['flags_var_name'] . '[' . $flag_name . ']"' . ($flag_value ? ' checked="checked"' : '') . ' />' . $GLOBALS['_labels'][$flag_name][1] . '</label></li>' . "\n";
                            }
                        }
                        ?>
                    </ul>
                </form>
                <!-- The least you could do is leave this link back as it is. This software is provided for free and I ask nothing in return except that you leave this link intact
                You're more likely to recieve support should you require some if I see a link back in your installation than if not -->
                <div id="footer"><a href="http://whitefyre.com/poxy/">PHProxy</a> <?php echo $GLOBALS['_version'] ?></div>
            </div>
        </body>
        </html>

    <?php
    exit(0);
}

function add_cookie($name, $value, $expires = 0)
{
    return rawurlencode(rawurlencode($name)) . '=' . rawurlencode(rawurlencode($value)) . (empty($expires) ? '' : '; expires=' . gmdate('D, d-M-Y H:i:s \G\M\T', $expires)) . '; path=/; domain=.' . $GLOBALS['_http_host'];
}

function set_post_vars($array, $parent_key = null)
{
    $temp = array();

    foreach ($array as $key => $value)
    {
        $key = isset($parent_key) ? sprintf('%s[%s]', $parent_key, urlencode($key)) : urlencode($key);
        if (is_array($value))
        {
            $temp = array_merge($temp, set_post_vars($value, $key));
        }
        else
        {
            $temp[$key] = urlencode($value);
        }
    }

    return $temp;
}

function set_post_files($array, $parent_key = null)
{
    $temp = array();

    foreach ($array as $key => $value)
    {
        $key = isset($parent_key) ? sprintf('%s[%s]', $parent_key, urlencode($key)) : urlencode($key);
        if (is_array($value))
        {
            $temp = array_merge_recursive($temp, set_post_files($value, $key));
        }
        else if (preg_match('#^([^\[\]]+)\[(name|type|tmp_name)\]#', $key, $m))
        {
            $temp[str_replace($m[0], $m[1], $key)][$m[2]] = $value;
        }
    }

    return $temp;
}

function url_parse($url, & $container)
{
    $temp = @parse_url($url);

    if (!empty($temp))
    {
        $temp['port_ext'] = '';
        $temp['base']     = $temp['scheme'] . '://' . $temp['host'];

        if (isset($temp['port']))
        {
            $temp['base'] .= $temp['port_ext'] = ':' . $temp['port'];
        }
        else
        {
            $temp['port'] = $temp['scheme'] === 'https' ? 443 : 80;
        }

        $temp['path'] = isset($temp['path']) ? $temp['path'] : '/';
        $path         = array();
        $temp['path'] = explode('/', $temp['path']);

        foreach ($temp['path'] as $dir)
        {
            if ($dir === '..')
            {
                array_pop($path);
            }
            else if ($dir !== '.')
            {
                for ($dir = rawurldecode($dir), $new_dir = '', $i = 0, $count_i = strlen($dir); $i < $count_i; $new_dir .= strspn($dir{$i}, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$-_.+!*\'(),?:@&;=') ? $dir{$i} : rawurlencode($dir{$i}), ++$i);
                $path[] = $new_dir;
            }
        }

        $temp['path']     = str_replace('/%7E', '/~', '/' . ltrim(implode('/', $path), '/'));
        $temp['file']     = substr($temp['path'], strrpos($temp['path'], '/')+1);
        $temp['dir']      = substr($temp['path'], 0, strrpos($temp['path'], '/'));
        $temp['base']    .= $temp['dir'];
        $temp['prev_dir'] = substr_count($temp['path'], '/') > 1 ? substr($temp['base'], 0, strrpos($temp['base'], '/')+1) : $temp['base'] . '/';
        $container = $temp;

        return true;
    }

    return false;
}

function complete_url($url, $proxify = true)
{
    $url = trim($url);

    if ($url === '')
    {
        return '';
    }

    $hash_pos = strrpos($url, '#');
    $fragment = $hash_pos !== false ? '#' . substr($url, $hash_pos) : '';
    $sep_pos  = strpos($url, '://');

    if ($sep_pos === false || $sep_pos > 5)
    {
        switch ($url{0})
        {
            case '/':
                $url = substr($url, 0, 2) === '//' ? $GLOBALS['_base']['scheme'] . ':' . $url : $GLOBALS['_base']['scheme'] . '://' . $GLOBALS['_base']['host'] . $GLOBALS['_base']['port_ext'] . $url;
                break;
            case '?':
                $url = $GLOBALS['_base']['base'] . '/' . $GLOBALS['_base']['file'] . $url;
                break;
            case '#':
                $proxify = false;
                break;
            case 'm':
                if (substr($url, 0, 7) == 'mailto:')
                {
                    $proxify = false;
                    break;
                }
            default:
                $url = $GLOBALS['_base']['base'] . '/' . $url;
        }
    }

    return $proxify ? "{$GLOBALS['_script_url']}?{$GLOBALS['_config']['url_var_name']}=" . encode_url($url) . $fragment : $url;
}

function proxify_inline_css($css)
{
    preg_match_all('#url\s*\(\s*(([^)]*(\\\))*[^)]*)(\)|$)?#i', $css, $matches, PREG_SET_ORDER);

    for ($i = 0, $count = count($matches); $i < $count; ++$i)
    {
        $css = str_replace($matches[$i][0], 'url(' . proxify_css_url($matches[$i][1]) . ')', $css);
    }

    return $css;
}

function proxify_css($css)
{
    $css = proxify_inline_css($css);

    preg_match_all("#@import\s*(?:\"([^\">]*)\"?|'([^'>]*)'?)([^;]*)(;|$)#i", $css, $matches, PREG_SET_ORDER);

    for ($i = 0, $count = count($matches); $i < $count; ++$i)
    {
        $delim = '"';
        $url   = $matches[$i][2];

        if (isset($matches[$i][3]))
        {
            $delim = "'";
            $url = $matches[$i][3];
        }

        $css = str_replace($matches[$i][0], '@import ' . $delim . proxify_css_url($matches[$i][1]) . $delim . (isset($matches[$i][4]) ? $matches[$i][4] : ''), $css);
    }

    return $css;
}

function proxify_css_url($url)
{
    $url   = trim($url);
    $delim = strpos($url, '"') === 0 ? '"' : (strpos($url, "'") === 0 ? "'" : '');

    return $delim . preg_replace('#([\(\),\s\'"\\\])#', '\\$1', complete_url(trim(preg_replace('#\\\(.)#', '$1', trim($url, $delim))))) . $delim;
}

//
// SET FLAGS
//

if (isset($_POST[$_config['url_var_name']]) && !isset($_GET[$_config['url_var_name']]) && isset($_POST[$_config['flags_var_name']]))
{
    foreach ($_flags as $flag_name => $flag_value)
    {
        $_iflags .= isset($_POST[$_config['flags_var_name']][$flag_name]) ? (string)(int)(bool)$_POST[$_config['flags_var_name']][$flag_name] : ($_frozen_flags[$flag_name] ? $flag_value : '0');
    }

    $_iflags = base_convert(($_iflags != '' ? $_iflags : '0'), 2, 16);
}
else if (isset($_GET[$_config['flags_var_name']]) && !isset($_GET[$_config['get_form_name']]) && ctype_alnum($_GET[$_config['flags_var_name']]))
{
    $_iflags = $_GET[$_config['flags_var_name']];
}
else if (isset($_COOKIE['flags']) && ctype_alnum($_COOKIE['flags']))
{
    $_iflags = $_COOKIE['flags'];
}

if ($_iflags !== '')
{
    $_set_cookie[] = add_cookie('flags', $_iflags, time()+2419200);
    $_iflags = str_pad(base_convert($_iflags, 16, 2), count($_flags), '0', STR_PAD_LEFT);
    $i = 0;

    foreach ($_flags as $flag_name => $flag_value)
    {
        $_flags[$flag_name] = $_frozen_flags[$flag_name] ? $flag_value : (int)(bool)$_iflags{$i};
        $i++;
    }
}

//
// DETERMINE URL-ENCODING BASED ON FLAGS
//

if ($_flags['rotate13'])
{
    function encode_url($url)
    {
        return rawurlencode(str_rot13($url));
    }
    function decode_url($url)
    {
        return str_replace(array('&amp;', '&#38;'), '&', str_rot13(rawurldecode($url)));
    }
}
else if ($_flags['base64_encode'])
{
    function encode_url($url)
    {
        return rawurlencode(base64_encode($url));
    }
    function decode_url($url)
    {
        return str_replace(array('&amp;', '&#38;'), '&', base64_decode(rawurldecode($url)));
    }
}
else
{
    function encode_url($url)
    {
        return rawurlencode($url);
    }
    function decode_url($url)
    {
        return str_replace(array('&amp;', '&#38;'), '&', rawurldecode($url));
    }
}

//
// COMPRESS OUTPUT IF INSTRUCTED
//

if ($_config['compress_output'] && $_system['gzip'])
{
    ob_start('ob_gzhandler');
}

//
// STRIP SLASHES FROM GPC IF NECESSARY
//

if ($_system['stripslashes'])
{
    function _stripslashes($value)
    {
        return is_array($value) ? array_map('_stripslashes', $value) : (is_string($value) ? stripslashes($value) : $value);
    }

    $_GET    = _stripslashes($_GET);
    $_POST   = _stripslashes($_POST);
    $_COOKIE = _stripslashes($_COOKIE);
}

//
// FIGURE OUT WHAT TO DO (POST URL-form submit, GET form request, regular request, basic auth, cookie manager, show URL-form)
//

if (isset($_POST[$_config['url_var_name']]) && !isset($_GET[$_config['url_var_name']]))
{
    header('Location: ' . $_script_url . '?' . $_config['url_var_name'] . '=' . encode_url($_POST[$_config['url_var_name']]) . '&' . $_config['flags_var_name'] . '=' . base_convert($_iflags, 2, 16));
    exit(0);
}

if (isset($_GET[$_config['get_form_name']]))
{
    $_url  = decode_url($_GET[$_config['get_form_name']]);
    $qstr = strpos($_url, '?') !== false ? (strpos($_url, '?') === strlen($_url)-1 ? '' : '&') : '?';
    $arr  = explode('&', $_SERVER['QUERY_STRING']);

    if (preg_match('#^\Q' . $_config['get_form_name'] . '\E#', $arr[0]))
    {
        array_shift($arr);
    }

    $_url .= $qstr . implode('&', $arr);
}
else if (isset($_GET[$_config['url_var_name']]))
{
    $_url = decode_url($_GET[$_config['url_var_name']]);
}
else if (isset($_GET['action']) && $_GET['action'] == 'cookies')
{
    show_report(array('which' => 'cookies'));
}
else
{
    show_report(array('which' => 'index', 'category' => 'entry_form'));
}

if (isset($_GET[$_config['url_var_name']], $_POST[$_config['basic_auth_var_name']], $_POST['username'], $_POST['password']))
{
    $_request_method    = 'GET';
    $_basic_auth_realm  = base64_decode($_POST[$_config['basic_auth_var_name']]);
    $_basic_auth_header = base64_encode($_POST['username'] . ':' . $_POST['password']);
}

//
// SET URL
//

if (strpos($_url, '://') === false)
{
    $_url = 'http://' . $_url;
}

if (url_parse($_url, $_url_parts))
{
    $_base = $_url_parts;

    if (!empty($_hosts))
    {
        foreach ($_hosts as $host)
        {
            if (preg_match($host, $_url_parts['host']))
            {
                show_report(array('which' => 'index', 'category' => 'error', 'group' => 'url', 'type' => 'external', 'error' => 1));
            }
        }
    }
}
else
{
    show_report(array('which' => 'index', 'category' => 'error', 'group' => 'url', 'type' => 'external', 'error' => 2));
}

//
// HOTLINKING PREVENTION
//

if (!$_config['allow_hotlinking'] && isset($_SERVER['HTTP_REFERER']))
{
    $_hotlink_domains[] = $_http_host;
    $is_hotlinking      = true;

    foreach ($_hotlink_domains as $host)
    {
        if (preg_match('#^https?\:\/\/(www)?\Q' . $host  . '\E(\/|\:|$)#i', trim($_SERVER['HTTP_REFERER'])))
        {
            $is_hotlinking = false;
            break;
        }
    }

    if ($is_hotlinking)
    {
        switch ($_config['upon_hotlink'])
        {
            case 1:
                show_report(array('which' => 'index', 'category' => 'error', 'group' => 'resource', 'type' => 'hotlinking'));
                break;
            case 2:
                header('HTTP/1.0 404 Not Found');
                exit(0);
            default:
                header('Location: ' . $_config['upon_hotlink']);
                exit(0);
        }
    }
}

//
// OPEN SOCKET TO SERVER
//

do
{
    $_retry  = false;
    $_socket = @fsockopen(($_url_parts['scheme'] === 'https' && $_system['ssl'] ? 'ssl://' : 'tcp://') . $_url_parts['host'], $_url_parts['port'], $err_no, $err_str, 30);

    if ($_socket === false)
    {
        show_report(array('which' => 'index', 'category' => 'error', 'group' => 'url', 'type' => 'internal', 'error' => $err_no));
    }

    //
    // SET REQUEST HEADERS
    //

    $_request_headers  = $_request_method . ' ' . $_url_parts['path'];

    if (isset($_url_parts['query']))
    {
        $_request_headers .= '?';
        $query = preg_split('#([&;])#', $_url_parts['query'], -1, PREG_SPLIT_DELIM_CAPTURE);
        for ($i = 0, $count = count($query); $i < $count; $_request_headers .= implode('=', array_map('urlencode', array_map('urldecode', explode('=', $query[$i])))) . (isset($query[++$i]) ? $query[$i] : ''), $i++);
    }

    $_request_headers .= " HTTP/1.0\r\n";
    $_request_headers .= 'Host: ' . $_url_parts['host'] . $_url_parts['port_ext'] . "\r\n";

    if (isset($_SERVER['HTTP_USER_AGENT']))
    {
        $_request_headers .= 'User-Agent: ' . $_SERVER['HTTP_USER_AGENT'] . "\r\n";
    }
    if (isset($_SERVER['HTTP_ACCEPT']))
    {
        $_request_headers .= 'Accept: ' . $_SERVER['HTTP_ACCEPT'] . "\r\n";
    }
    else
    {
        $_request_headers .= "Accept: */*;q=0.1\r\n";
    }
    if ($_flags['show_referer'] && isset($_SERVER['HTTP_REFERER']) && preg_match('#^\Q' . $_script_url . '?' . $_config['url_var_name'] . '=\E([^&]+)#', $_SERVER['HTTP_REFERER'], $matches))
    {
        $_request_headers .= 'Referer: ' . decode_url($matches[1]) . "\r\n";
    }
    if (!empty($_COOKIE))
    {
        $_cookie  = '';
        $_auth_creds    = array();

        foreach ($_COOKIE as $cookie_id => $cookie_content)
        {
            $cookie_id      = explode(';', rawurldecode($cookie_id));
            $cookie_content = explode(';', rawurldecode($cookie_content));

            if ($cookie_id[0] === 'COOKIE')
            {
                $cookie_id[3] = str_replace('_', '.', $cookie_id[3]); //stupid PHP can't have dots in var names

                if (count($cookie_id) < 4 || ($cookie_content[1] == 'secure' && $_url_parts['scheme'] != 'https'))
                {
                    continue;
                }

                if ((preg_match('#\Q' . $cookie_id[3] . '\E$#i', $_url_parts['host']) || strtolower($cookie_id[3]) == strtolower('.' . $_url_parts['host'])) && preg_match('#^\Q' . $cookie_id[2] . '\E#', $_url_parts['path']))
                {
                    $_cookie .= ($_cookie != '' ? '; ' : '') . (empty($cookie_id[1]) ? '' : $cookie_id[1] . '=') . $cookie_content[0];
                }
            }
            else if ($cookie_id[0] === 'AUTH' && count($cookie_id) === 3)
            {
                $cookie_id[2] = str_replace('_', '.', $cookie_id[2]);

                if ($_url_parts['host'] . ':' . $_url_parts['port'] === $cookie_id[2])
                {
                    $_auth_creds[$cookie_id[1]] = $cookie_content[0];
                }
            }
        }

        if ($_cookie != '')
        {
            $_request_headers .= "Cookie: $_cookie\r\n";
        }
    }
    if (isset($_url_parts['user'], $_url_parts['pass']))
    {
        $_basic_auth_header = base64_encode($_url_parts['user'] . ':' . $_url_parts['pass']);
    }
    if (!empty($_basic_auth_header))
    {
        $_set_cookie[] = add_cookie("AUTH;{$_basic_auth_realm};{$_url_parts['host']}:{$_url_parts['port']}", $_basic_auth_header);
        $_request_headers .= "Authorization: Basic {$_basic_auth_header}\r\n";
    }
    else if (!empty($_basic_auth_realm) && isset($_auth_creds[$_basic_auth_realm]))
    {
        $_request_headers  .= "Authorization: Basic {$_auth_creds[$_basic_auth_realm]}\r\n";
    }
    else if (list($_basic_auth_realm, $_basic_auth_header) = each($_auth_creds))
    {
        $_request_headers .= "Authorization: Basic {$_basic_auth_header}\r\n";
    }
    if ($_request_method == 'POST')
    {
        if (!empty($_FILES) && $_system['uploads'])
        {
            $_data_boundary = '----' . md5(uniqid(rand(), true));
            $array = set_post_vars($_POST);

            foreach ($array as $key => $value)
            {
                $_post_body .= "--{$_data_boundary}\r\n";
                $_post_body .= "Content-Disposition: form-data; name=\"$key\"\r\n\r\n";
                $_post_body .= urldecode($value) . "\r\n";
            }

            $array = set_post_files($_FILES);

            foreach ($array as $key => $file_info)
            {
                $_post_body .= "--{$_data_boundary}\r\n";
                $_post_body .= "Content-Disposition: form-data; name=\"$key\"; filename=\"{$file_info['name']}\"\r\n";
                $_post_body .= 'Content-Type: ' . (empty($file_info['type']) ? 'application/octet-stream' : $file_info['type']) . "\r\n\r\n";

                if (is_readable($file_info['tmp_name']))
                {
                    $handle = fopen($file_info['tmp_name'], 'rb');
                    $_post_body .= fread($handle, filesize($file_info['tmp_name']));
                    fclose($handle);
                }

                $_post_body .= "\r\n";
            }

            $_post_body       .= "--{$_data_boundary}--\r\n";
            $_request_headers .= "Content-Type: multipart/form-data; boundary={$_data_boundary}\r\n";
            $_request_headers .= "Content-Length: " . strlen($_post_body) . "\r\n\r\n";
            $_request_headers .= $_post_body;
        }
        else
        {
            $array = set_post_vars($_POST);

            foreach ($array as $key => $value)
            {
                $_post_body .= !empty($_post_body) ? '&' : '';
                $_post_body .= $key . '=' . $value;
            }
            $_request_headers .= "Content-Type: application/x-www-form-urlencoded\r\n";
            $_request_headers .= "Content-Length: " . strlen($_post_body) . "\r\n\r\n";
            $_request_headers .= $_post_body;
            $_request_headers .= "\r\n";
        }

        $_post_body = '';
    }
    else
    {
        $_request_headers .= "\r\n";
    }

    fwrite($_socket, $_request_headers);

    //
    // PROCESS RESPONSE HEADERS
    //

    $_response_headers = $_response_keys = array();

    $line = fgets($_socket, 8192);

    while (strspn($line, "\r\n") !== strlen($line))
    {
        @list($name, $value) = explode(':', $line, 2);
        $name = trim($name);
        $_response_headers[strtolower($name)][] = trim($value);
        $_response_keys[strtolower($name)] = $name;
        $line = fgets($_socket, 8192);
    }

    sscanf(current($_response_keys), '%s %s', $_http_version, $_response_code);

    if (isset($_response_headers['content-type']))
    {
        list($_content_type, ) = explode(';', str_replace(' ', '', strtolower($_response_headers['content-type'][0])), 2);
    }
    if (isset($_response_headers['content-length']))
    {
        $_content_length = $_response_headers['content-length'][0];
        unset($_response_headers['content-length'], $_response_keys['content-length']);
    }
    if (isset($_response_headers['content-disposition']))
    {
        $_content_disp = $_response_headers['content-disposition'][0];
        unset($_response_headers['content-disposition'], $_response_keys['content-disposition']);
    }
    if (isset($_response_headers['set-cookie']) && $_flags['accept_cookies'])
    {
        foreach ($_response_headers['set-cookie'] as $cookie)
        {
            $name = $value = $expires = $path = $domain = $secure = $expires_time = '';

            preg_match('#^\s*([^=;,\s]*)\s*=?\s*([^;]*)#',  $cookie, $match) && list(, $name, $value) = $match;
            preg_match('#;\s*expires\s*=\s*([^;]*)#i',      $cookie, $match) && list(, $expires)      = $match;
            preg_match('#;\s*path\s*=\s*([^;,\s]*)#i',      $cookie, $match) && list(, $path)         = $match;
            preg_match('#;\s*domain\s*=\s*([^;,\s]*)#i',    $cookie, $match) && list(, $domain)       = $match;
            preg_match('#;\s*(secure\b)#i',                 $cookie, $match) && list(, $secure)       = $match;

            $expires_time = empty($expires) ? 0 : intval(@strtotime($expires));
            $expires = ($_flags['session_cookies'] && !empty($expires) && time()-$expires_time < 0) ? '' : $expires;
            $path    = empty($path)   ? '/' : $path;

            if (empty($domain))
            {
                $domain = $_url_parts['host'];
            }
            else
            {
                $domain = '.' . strtolower(str_replace('..', '.', trim($domain, '.')));

                if ((!preg_match('#\Q' . $domain . '\E$#i', $_url_parts['host']) && $domain != '.' . $_url_parts['host']) || (substr_count($domain, '.') < 2 && $domain{0} == '.'))
                {
                    continue;
                }
            }
            if (count($_COOKIE) >= 15 && time()-$expires_time <= 0)
            {
                $_set_cookie[] = add_cookie(current($_COOKIE), '', 1);
            }

            $_set_cookie[] = add_cookie("COOKIE;$name;$path;$domain", "$value;$secure", $expires_time);
        }
    }
    if (isset($_response_headers['set-cookie']))
    {
        unset($_response_headers['set-cookie'], $_response_keys['set-cookie']);
    }
    if (!empty($_set_cookie))
    {
        $_response_keys['set-cookie'] = 'Set-Cookie';
        $_response_headers['set-cookie'] = $_set_cookie;
    }
    if (isset($_response_headers['p3p']) && preg_match('#policyref\s*=\s*[\'"]?([^\'"\s]*)[\'"]?#i', $_response_headers['p3p'][0], $matches))
    {
        $_response_headers['p3p'][0] = str_replace($matches[0], 'policyref="' . complete_url($matches[1]) . '"', $_response_headers['p3p'][0]);
    }
    if (isset($_response_headers['refresh']) && preg_match('#([0-9\s]*;\s*URL\s*=)\s*(\S*)#i', $_response_headers['refresh'][0], $matches))
    {
        $_response_headers['refresh'][0] = $matches[1] . complete_url($matches[2]);
    }
    if (isset($_response_headers['location']))
    {
        $_response_headers['location'][0] = complete_url($_response_headers['location'][0]);
    }
    if (isset($_response_headers['uri']))
    {
        $_response_headers['uri'][0] = complete_url($_response_headers['uri'][0]);
    }
    if (isset($_response_headers['content-location']))
    {
        $_response_headers['content-location'][0] = complete_url($_response_headers['content-location'][0]);
    }
    if (isset($_response_headers['connection']))
    {
        unset($_response_headers['connection'], $_response_keys['connection']);
    }
    if (isset($_response_headers['keep-alive']))
    {
        unset($_response_headers['keep-alive'], $_response_keys['keep-alive']);
    }
    if ($_response_code == 401 && isset($_response_headers['www-authenticate']) && preg_match('#basic\s+(?:realm="(.*?)")?#i', $_response_headers['www-authenticate'][0], $matches))
    {
        if (isset($_auth_creds[$matches[1]]) && !$_quit)
        {
            $_basic_auth_realm  = $matches[1];
            $_basic_auth_header = '';
            $_retry = $_quit = true;
        }
        else
        {
            show_report(array('which' => 'index', 'category' => 'auth', 'realm' => $matches[1]));
        }
    }
}
while ($_retry);

//
// OUTPUT RESPONSE IF NO PROXIFICATION IS NEEDED
//

if (!isset($_proxify[$_content_type]))
{
    @set_time_limit(0);

    $_response_keys['content-disposition'] = 'Content-Disposition';
    $_response_headers['content-disposition'][0] = empty($_content_disp) ? ($_content_type == 'application/octet_stream' ? 'attachment' : 'inline') . '; filename="' . $_url_parts['file'] . '"' : $_content_disp;

    if ($_content_length !== false)
    {
        if ($_config['max_file_size'] != -1 && $_content_length > $_config['max_file_size'])
        {
            show_report(array('which' => 'index', 'category' => 'error', 'group' => 'resource', 'type' => 'file_size'));
        }

        $_response_keys['content-length'] = 'Content-Length';
        $_response_headers['content-length'][0] = $_content_length;
    }

    $_response_headers   = array_filter($_response_headers);
    $_response_keys      = array_filter($_response_keys);

    header(array_shift($_response_keys));
    array_shift($_response_headers);

    foreach ($_response_headers as $name => $array)
    {
        foreach ($array as $value)
        {
            header($_response_keys[$name] . ': ' . $value, false);
        }
    }

    do
    {
        $data = fread($_socket, 8192);
        echo $data;
    }
    while (isset($data{0}));

    fclose($_socket);
    exit(0);
}

do
{
    $data = @fread($_socket, 8192); // silenced to avoid the "normal" warning by a faulty SSL connection
    $_response_body .= $data;
}
while (isset($data{0}));

unset($data);
fclose($_socket);

//
// MODIFY AND DUMP RESOURCE
//

if ($_content_type == 'text/css')
{
    $_response_body = proxify_css($_response_body);
}
else
{
    if ($_flags['strip_title'])
    {
        $_response_body = preg_replace('#(<\s*title[^>]*>)(.*?)(<\s*/title[^>]*>)#is', '$1$3', $_response_body);
    }
    if ($_flags['remove_scripts'])
    {
        $_response_body = preg_replace('#<\s*script[^>]*?>.*?<\s*/\s*script\s*>#si', '', $_response_body);
        $_response_body = preg_replace("#(\bon[a-z]+)\s*=\s*(?:\"([^\"]*)\"?|'([^']*)'?|([^'\"\s>]*))?#i", '', $_response_body);
        $_response_body = preg_replace('#<noscript>(.*?)</noscript>#si', "$1", $_response_body);
    }
    if (!$_flags['show_images'])
    {
        $_response_body = preg_replace('#<(img|image)[^>]*?>#si', '', $_response_body);
    }

    //
    // PROXIFY HTML RESOURCE
    //

    $tags = array
    (
        'a'          => array('href'),
        'img'        => array('src', 'longdesc'),
        'image'      => array('src', 'longdesc'),
        'body'       => array('background'),
        'base'       => array('href'),
        'frame'      => array('src', 'longdesc'),
        'iframe'     => array('src', 'longdesc'),
        'head'       => array('profile'),
        'layer'      => array('src'),
        'input'      => array('src', 'usemap'),
        'form'       => array('action'),
        'area'       => array('href'),
        'link'       => array('href', 'src', 'urn'),
        'meta'       => array('content'),
        'param'      => array('value'),
        'applet'     => array('codebase', 'code', 'object', 'archive'),
        'object'     => array('usermap', 'codebase', 'classid', 'archive', 'data'),
        'script'     => array('src'),
        'select'     => array('src'),
        'hr'         => array('src'),
        'table'      => array('background'),
        'tr'         => array('background'),
        'th'         => array('background'),
        'td'         => array('background'),
        'bgsound'    => array('src'),
        'blockquote' => array('cite'),
        'del'        => array('cite'),
        'embed'      => array('src'),
        'fig'        => array('src', 'imagemap'),
        'ilayer'     => array('src'),
        'ins'        => array('cite'),
        'note'       => array('src'),
        'overlay'    => array('src', 'imagemap'),
        'q'          => array('cite'),
        'ul'         => array('src')
    );

    preg_match_all('#(<\s*style[^>]*>)(.*?)(<\s*/\s*style[^>]*>)#is', $_response_body, $matches, PREG_SET_ORDER);

    for ($i = 0, $count_i = count($matches); $i < $count_i; ++$i)
    {
        $_response_body = str_replace($matches[$i][0], $matches[$i][1]. proxify_css($matches[$i][2]) .$matches[$i][3], $_response_body);
    }

    preg_match_all("#<\s*([a-zA-Z\?-]+)([^>]+)>#S", $_response_body, $matches);

    for ($i = 0, $count_i = count($matches[0]); $i < $count_i; ++$i)
    {
        if (!preg_match_all("#([a-zA-Z\-\/]+)\s*(?:=\s*(?:\"([^\">]*)\"?|'([^'>]*)'?|([^'\"\s]*)))?#S", $matches[2][$i], $m, PREG_SET_ORDER))
        {
            continue;
        }

        $rebuild    = false;
        $extra_html = $temp = '';
        $attrs      = array();

        for ($j = 0, $count_j = count($m); $j < $count_j; $attrs[strtolower($m[$j][1])] = (isset($m[$j][4]) ? $m[$j][4] : (isset($m[$j][3]) ? $m[$j][3] : (isset($m[$j][2]) ? $m[$j][2] : false))), ++$j);

        if (isset($attrs['style']))
        {
            $rebuild = true;
            $attrs['style'] = proxify_inline_css($attrs['style']);
        }

        $tag = strtolower($matches[1][$i]);

        if (isset($tags[$tag]))
        {
            switch ($tag)
            {
                case 'a':
                    if (isset($attrs['href']))
                    {
                        $rebuild = true;
                        $attrs['href'] = complete_url($attrs['href']);
                    }
                    break;
                case 'img':
                    if (isset($attrs['src']))
                    {
                        $rebuild = true;
                        $attrs['src'] = complete_url($attrs['src']);
                    }
                    if (isset($attrs['longdesc']))
                    {
                        $rebuild = true;
                        $attrs['longdesc'] = complete_url($attrs['longdesc']);
                    }
                    break;
                case 'form':
                    if (isset($attrs['action']))
                    {
                        $rebuild = true;

                        if (trim($attrs['action']) === '')
                        {
                            $attrs['action'] = $_url_parts['path'];
                        }
                        if (!isset($attrs['method']) || strtolower(trim($attrs['method'])) === 'get')
                        {
                            $extra_html = '<input type="hidden" name="' . $_config['get_form_name'] . '" value="' . encode_url(complete_url($attrs['action'], false)) . '" />';
                            $attrs['action'] = '';
                            break;
                        }

                        $attrs['action'] = complete_url($attrs['action']);
                    }
                    break;
                case 'base':
                    if (isset($attrs['href']))
                    {
                        $rebuild = true;
                        url_parse($attrs['href'], $_base);
                        $attrs['href'] = complete_url($attrs['href']);
                    }
                    break;
                case 'meta':
                    if ($_flags['strip_meta'] && isset($attrs['name']))
                    {
                        $_response_body = str_replace($matches[0][$i], '', $_response_body);
                    }
                    if (isset($attrs['http-equiv'], $attrs['content']) && preg_match('#\s*refresh\s*#i', $attrs['http-equiv']))
                    {
                        if (preg_match('#^(\s*[0-9]*\s*;\s*url=)(.*)#i', $attrs['content'], $content))
                        {
                            $rebuild = true;
                            $attrs['content'] =  $content[1] . complete_url(trim($content[2], '"\''));
                        }
                    }
                    break;
                case 'head':
                    if (isset($attrs['profile']))
                    {
                        $rebuild = true;
                        $attrs['profile'] = implode(' ', array_map('complete_url', explode(' ', $attrs['profile'])));
                    }
                    break;
                case 'applet':
                    if (isset($attrs['codebase']))
                    {
                        $rebuild = true;
                        $temp = $_base;
                        url_parse(complete_url(rtrim($attrs['codebase'], '/') . '/', false), $_base);
                        unset($attrs['codebase']);
                    }
                    if (isset($attrs['code']) && strpos($attrs['code'], '/') !== false)
                    {
                        $rebuild = true;
                        $attrs['code'] = complete_url($attrs['code']);
                    }
                    if (isset($attrs['object']))
                    {
                        $rebuild = true;
                        $attrs['object'] = complete_url($attrs['object']);
                    }
                    if (isset($attrs['archive']))
                    {
                        $rebuild = true;
                        $attrs['archive'] = implode(',', array_map('complete_url', preg_split('#\s*,\s*#', $attrs['archive'])));
                    }
                    if (!empty($temp))
                    {
                        $_base = $temp;
                    }
                    break;
                case 'object':
                    if (isset($attrs['usemap']))
                    {
                        $rebuild = true;
                        $attrs['usemap'] = complete_url($attrs['usemap']);
                    }
                    if (isset($attrs['codebase']))
                    {
                        $rebuild = true;
                        $temp = $_base;
                        url_parse(complete_url(rtrim($attrs['codebase'], '/') . '/', false), $_base);
                        unset($attrs['codebase']);
                    }
                    if (isset($attrs['data']))
                    {
                        $rebuild = true;
                        $attrs['data'] = complete_url($attrs['data']);
                    }
                    if (isset($attrs['classid']) && !preg_match('#^clsid:#i', $attrs['classid']))
                    {
                        $rebuild = true;
                        $attrs['classid'] = complete_url($attrs['classid']);
                    }
                    if (isset($attrs['archive']))
                    {
                        $rebuild = true;
                        $attrs['archive'] = implode(' ', array_map('complete_url', explode(' ', $attrs['archive'])));
                    }
                    if (!empty($temp))
                    {
                        $_base = $temp;
                    }
                    break;
                case 'param':
                    if (isset($attrs['valuetype'], $attrs['value']) && strtolower($attrs['valuetype']) == 'ref' && preg_match('#^[\w.+-]+://#', $attrs['value']))
                    {
                        $rebuild = true;
                        $attrs['value'] = complete_url($attrs['value']);
                    }
                    break;
                case 'frame':
                case 'iframe':
                    if (isset($attrs['src']))
                    {
                        $rebuild = true;
                        $attrs['src'] = complete_url($attrs['src']) . '&nf=1';
                    }
                    if (isset($attrs['longdesc']))
                    {
                        $rebuild = true;
                        $attrs['longdesc'] = complete_url($attrs['longdesc']);
                    }
                    break;
                default:
                    foreach ($tags[$tag] as $attr)
                    {
                        if (isset($attrs[$attr]))
                        {
                            $rebuild = true;
                            $attrs[$attr] = complete_url($attrs[$attr]);
                        }
                    }
                    break;
            }
        }

        if ($rebuild)
        {
            $new_tag = "<$tag";
            foreach ($attrs as $name => $value)
            {
                $delim = strpos($value, '"') && !strpos($value, "'") ? "'" : '"';
                $new_tag .= ' ' . $name . ($value !== false ? '=' . $delim . $value . $delim : '');
            }

            $_response_body = str_replace($matches[0][$i], $new_tag . '>' . $extra_html, $_response_body);
        }
    }

    if ($_flags['include_form'] && !isset($_GET['nf']))
    {
        $_url_form      = '<div style="width:100%;margin:0;text-align:center;border-bottom:1px solid #725554;color:#000000;background-color:#F2FDF3;font-size:12px;font-weight:bold;font-family:Bitstream Vera Sans,arial,sans-serif;padding:4px;">'
                        . '<form method="post" action="' . $_script_url . '">'
                        . ' <label for="____' . $_config['url_var_name'] . '"><a href="' . $_url . '">Address</a>:</label> <input id="____' . $_config['url_var_name'] . '" type="text" size="80" name="' . $_config['url_var_name'] . '" value="' . $_url . '" />'
                        . ' <input type="submit" name="go" value="Go" />'
                        . ' [go: <a href="' . $_script_url . '?' . $_config['url_var_name'] . '=' . encode_url($_url_parts['prev_dir']) .' ">up one dir</a>, <a href="' . $_script_base . '">main page</a>]'
                        . '<br /><hr />';

        foreach ($_flags as $flag_name => $flag_value)
        {
            if (!$_frozen_flags[$flag_name])
            {
                $_url_form .= '<label><input type="checkbox" name="' . $_config['flags_var_name'] . '[' . $flag_name . ']"' . ($flag_value ? ' checked="checked"' : '') . ' /> ' . $_labels[$flag_name][0] . '</label> ';
            }
        }

        $_url_form .= '</form></div>';
        $_response_body = preg_replace('#\<\s*body(.*?)\>#si', "$0\n$_url_form" , $_response_body, 1);
    }
}

$_response_keys['content-disposition'] = 'Content-Disposition';
$_response_headers['content-disposition'][0] = empty($_content_disp) ? ($_content_type == 'application/octet_stream' ? 'attachment' : 'inline') . '; filename="' . $_url_parts['file'] . '"' : $_content_disp;
$_response_keys['content-length'] = 'Content-Length';
$_response_headers['content-length'][0] = strlen($_response_body);
$_response_headers   = array_filter($_response_headers);
$_response_keys      = array_filter($_response_keys);

header(array_shift($_response_keys));
array_shift($_response_headers);

foreach ($_response_headers as $name => $array)
{
    foreach ($array as $value)
    {
        header($_response_keys[$name] . ': ' . $value, false);
    }
}

echo $_response_body;
?>
