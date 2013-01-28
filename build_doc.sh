pushd doc/
LD_LIBRARY_PATH=/opt/local/lib:. python ../fontcreator.py -h > source/modules/options.txt
LD_LIBRARY_PATH=/opt/local/lib:. make html
popd
