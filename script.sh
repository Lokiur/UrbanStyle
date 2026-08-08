
sudo /opt/lampp/lampp start 2>/dev/null


test -d venv || echo "Creando entorno virtual"
test -d venv || python3 -m venv venv


test -n "$FISH_VERSION" && source venv/bin/activate.fish
test -z "$FISH_VERSION" && source venv/bin/activate
