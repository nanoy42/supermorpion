# SuperMorpion

## What is it ?

SuperMorpion is a bigger (and more interesting) version of the classic tic-tac-toe game. You can play at https://supermorpion.nanoy.fr.

## Installation

To install the game, you will need:

 * python3 and pip
 * postgresql
 * redis
 * some python dependencies

First thing is to clone the project:

```
git clone https://github.com/nanoy42/supermorpion
```

Then install the python dependencies:

```
pipenv install --ignore-pipfile
```

You can install the dev dependencies with :
```
pipenv install --dev --pre
```

Finally copy the final settings example file :
```
cp supermorpion/local_settings.example.py supermorpion/local_settings.py
```

and edit the file to adjust settings.
