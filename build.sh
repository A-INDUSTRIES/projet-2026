#!/usr/bin/env bash

if [[ ! -d ".venv" ]]; then
    echo ".venv does not exists, creating it"
    uv sync
fi

echo "Loading python environment"
source .venv/bin/activate

read -p "Clean old build? (Y/n): " clean

if [[ $clean == [Yy] ]]; then
    echo "Cleaning build directories"
    rm -r build/
    rm -r dist
fi

echo "Building app.."
pyinstaller -n communiquer_avec_les_yeux \
    --collect-all language_tags \
    --collect-all espeakng_loader \
    --collect-all kokoro \
    --collect-all phonemizer \
    --hidden-import charset_normalizer \
    --add-data app/assets:. \
    -F main.py
echo "Done!"