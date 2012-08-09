#!/bin/bash
pname=fifo_dispatcher.py

for i in `ps axu | grep $pname | grep -v "grep $pname" | awk '{printf("%d\n", $2)}' `
do
        kill $i
	#echo $i
done

echo "after kill"

ps aux | grep $pname
