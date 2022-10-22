echo "Cloning Repo, Please Wait..."
git clone https://github.com/sakhaavvaavaj93/krishnathulasi-.git /krishnathulasi-
echo "Installing Requirements..."
cd /krishnathulasi-
pip3 install -U -r requirements.txt
echo "Starting Bot, Please Wait..."
python3 main.py
