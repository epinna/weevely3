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
        php_binary, '-r', """function is_label($str) {
return preg_match('~[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*+~',$str);
}

function get_tiny($snippet,
$remove_whitespace=TRUE,
$remove_comments=TRUE) {

//generate tokens from snippet
$tokens = token_get_all($snippet);

//replace all variables, remove whitespace, remove comments
$new_source = '';
foreach ($tokens as $i => $token) {
  if(!is_array($token)) {
    $new_source .= $token;
    continue;
  }
  if($remove_comments) {
      if(in_array($token[0],array(T_COMMENT,T_DOC_COMMENT))) {
        continue;
      }
    }
  if ($token[0] == T_WHITESPACE && $remove_whitespace) {
    if (isset($tokens[$i-1]) && isset($tokens[$i+1]) && is_array($tokens[$i-1]) && is_array($tokens[$i+1]) && is_label($tokens[$i-1][1]) && is_label($tokens[$i+1][1])) {
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

$d=<<<'EOD'
%s
EOD;

print(get_tiny($d));
""" % ('<?php %s ?>' % str(original_code)),
    ])

    return output[6:-2]
