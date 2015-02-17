#!/usr/bin/gawk -f
{
	cnt += $1;
}

END {
	print cnt;
}
