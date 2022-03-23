# Update Mangas
A simple tool to update my notion's manga page. 

## Pre-requisites
Since I'm using match-case you need **Python3.10 or greater**.

## Usage
The script has to be executed with at least one argument. You can not execute the script with two or more different arguments
at the same time. Execute `python3 update-mangas.py [argument] -h` to see each argument usage.

The script has 4 different arguments:
+ ***all-shonen-jump***: adds 1 to the "Ultimo capi" property to all the shonen jump mangas. This was made because every sunday Sueisha's web, [mangaplus](https://mangaplus.shueisha.co.jp/updates), uploads 
the last chapter all of its mangas, and it was tedious to be doing it manually one by one. You can execute it with the `-i` flag to ignore one or more mangas (There are some weeks where a series is paused).

  - ```
    python3 update-mangas.py all-shonen-jump
    python3 update-mangas.py all-shonen-jump -i "One Piece" "Jujutsu Kaisen" ...
    ```

+ ***update-single***: adds 1 to the "Ultimo capi" property to a single manga. It was made for weekly series that are not from Shōnen Jump.
  - `python3 update-mangas.py update-single "One Punch Man"`
    
+ ***finished***: updates the "Terminado" property, therefore removing it from the main database view.
  - `python3 update-mangas.py finished "manga1" "manga2" ...`

+ ***list***: Display all the mangas (that are not finished) in a table format.  
  - `python3 update-mangas.py list`

