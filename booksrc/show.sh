#!/bin/bash
echo "查看当前进度"
tail /home/code/baizheshu/booksrc/nohup.out 
echo ""
echo "查看总进度"
cat -n /home/code/baizheshu/booksrc/part1/bookcount 
