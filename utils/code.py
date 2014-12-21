from core.loggers import log
from distutils import spawn
from core import messages
import subprocess

def minify_php(original_code):

    php_binary = spawn.find_executable('php')
    if not php_binary:
        raise Exception(messages.utils_code.minify_php_missing_binary)

    output = subprocess.check_output(
        [
        php_binary, '-r', """class tinyPhp {
public $php_excludes = array(
                      '$GLOBALS',
                      '$_SERVER',
                      '$_GET',
                      '$_POST',
                      '$_FILES',
                      '$_REQUEST',
                      '$_SESSION',
                      '$_ENV',
                      '$_COOKIE',
                      '$php_errormsg',
                      '$HTTP_RAW_POST_DATA',
                      '$http_response_header',
                      '$argc',
                      '$argv'
                      );

function is_label($str) {
return preg_match('~[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*+~',$str);
}

function get_tiny($snippet,
$replace_variables=FALSE,
$remove_whitespace=TRUE,
$remove_comments=TRUE,
$additional_excludes=array()) {

//create excluded variables array
$php_excludes = $this->php_excludes;
if(!empty($additional_excludes)) {
  $excludes = array_merge($php_excludes,$additional_excludes);
  $excludes = array_unique($excludes);
} else {
  $excludes = $php_excludes;
}

//generate tokens from snippet
$tokens = token_get_all($snippet);

//get all variables in snippet, remove comments
$variables = array();
$new_source = '';
foreach ($tokens as $token) {
  if(!is_array($token)) {
    $new_source .= $token;
    continue;
  }
  if($token[0]==T_VARIABLE && !in_array($token[1],$excludes)) {
    $variables[] = $token[1];
  }
  if($remove_comments) {
    if(in_array($token[0],array(T_COMMENT,T_DOC_COMMENT))) {
      continue;
    }
  }
  $new_source .= $token[1];
}
$variables = array_unique($variables);

//generate replace values for all variables
if(!empty($variables)) {
  $replace_values = array();
  $count = 0;
  while($variable = current($variables)) {
    $mod = $count%%26;

    $repeat_chars = ((int)floor($count/26))+1;

    $replace_int = 97+$mod;
    $replace_value = chr(36);

    for($i=1;$i<=$repeat_chars;$i++) {
      $replace_value .= chr($replace_int);
    }

    if(!in_array($replace_value,$variables) && !in_array($replace_value,$excludes)) {
      $variable_replace[$variable] = $replace_value;
      next($variables);
    }
    $count++;
  }
}

//get all tokens from previous iteration
$tokens = token_get_all($new_source);

//replace all variables, remove whitespace
$new_source = '';
foreach ($tokens as $i => $token) {
  if(!is_array($token)) {
    $new_source .= $token;
    continue;
  }
  if($replace_variables) {
    if($token[0] == T_VARIABLE && !in_array($token[1],$excludes)) {
      $key = $token[1];
      $new_source .= $variable_replace[$key];
      continue;
    }
  }
  if ($token[0] == T_WHITESPACE && $remove_whitespace) {
    if (isset($tokens[$i-1]) && isset($tokens[$i+1]) && is_array($tokens[$i-1]) && is_array($tokens[$i+1]) && $this->is_label($tokens[$i-1][1]) && $this->is_label($tokens[$i+1][1])) {
      $new_source .= ' ';
    }
  } elseif($token[0]==T_CASE) {
    $new_source .= $token[1].' ';
  } else {
    $new_source .= $token[1];
  }
}
return $new_source;
}
}

$d=<<<'EOD'
%s
EOD;

$tp = new tinyPhp();
print($tp->get_tiny($d));
""" % ('<?php %s ?>' % str(original_code)),
    ])

    return output[6:-2]
