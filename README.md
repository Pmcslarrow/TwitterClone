![Python Build](https://github.com/Pmcslarrow/TwitterClone/actions/workflows/python-build.yml/badge.svg)

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/ZvQj6fur)

### Running the front-end tests locally
1) Clone the repo
```
git clone https://github.com/Pmcslarrow/TwitterClone.git
```
2) Navigate to the repo in the terminal
```
cd TwitterClone/
```
3) Install [nvm](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating) (Node Version Manager)
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```
```
source ~/.bashrc    # or use ~/.zshrc if you're using zsh
```
4) Install and select Node.js v20
```
nvm install 20
nvm use 20
nvm alias default 20
```
5) Navigate to the front-end directory
```
cd twitter_clone/
```
6) Install dependencies
```
npm install
```
7) Run
```
npm run test
```

### Running the front-end locally
1) Follow the steps above up until step 6.
2) Run
```
npm run dev
```
3) Open the URL shown after "Local:" in your preffered browser.

### Running the back-end tests locally
1) Clone the repo
```
git clone https://github.com/Pmcslarrow/TwitterClone.git
```
2) Navigate to the repo in the terminal
```
cd TwitterClone/
```
3) Build the virtual environment
```
python3.13 -m venv twitter_clone.env
```
4) Activate the environment
```
source twitter_clone.env/bin/activate
```
5) Install packages
```
pip install -r requirements.txt
```
6) Setup
```
bash setup_bash_mac.sh
```
7) Spin-up the docker container with the MySQL database and run tests
```
./refresh.sh
```
8) Stop the docker container
```
./stop-container.sh
```
