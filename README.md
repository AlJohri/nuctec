# nuctec

## Usage
```
workon nuctec
python scrape.py
python driver.py
```

-----------------------------------

## Setup
```
mkvirtualenv nuctec
pip install -r requirements.txt
```

## Pre-Setup
```
brew install r mongodb pyenv pyenv-virtualenvwrapper
ln -s /usr/local/opt/mongodb/*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mongodb.plist
pyenv install 2.7.8
pyenv global 2.7.8
```

### Add this to your rc file
```
if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi
pyenv virtualenvwrapper
```