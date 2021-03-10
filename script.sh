rm init.json init1.json init2.json

python3.8 saml.py

cat init.json | cut -c 9- | rev | cut -c 4- | rev > init1.json
sed 's/\\//g' init1.json > init2.json && rm init.json init1.json

python3.8 script.py