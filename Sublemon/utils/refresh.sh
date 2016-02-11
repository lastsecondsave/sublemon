cd "$(dirname $0)/../.."
ROOT_DIR=$(pwd)

for spy in $(find Sublemon -name '*.settings.py'); do
  cd "$ROOT_DIR/$(dirname $spy)"
  spy=$(basename $spy)
  echo "\nRunning $spy in $(pwd)\n"
  python $spy
done;

cd "$ROOT_DIR/Disco/build"
echo "\nRunning disco.py in $(pwd)\n"
python disco.py
