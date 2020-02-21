BEGIN { RS=""; FS="\n"; OFS=":" }
{ split($2, time,/\ -->\ /) }
{ gsub(/\r\n/," ",$0) }
{ print $1, time[1], time[2], $3 }
