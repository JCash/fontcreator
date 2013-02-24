pushd doc/
rm -rf build/
LD_LIBRARY_PATH=/opt/local/lib:. python ../fontcreator.py -h > source/modules/options.txt
LD_LIBRARY_PATH=/opt/local/lib:. make html
popd

rm doc.zip
zip -rq doc.zip doc/build/html/
