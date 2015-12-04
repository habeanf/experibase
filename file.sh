if test -n "$(find . -maxdepth 1 -name 'devo*' -print -quit)"
then
    echo found
else
    echo not found
fi
