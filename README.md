# mangaDL
Download manga/comic from command line

usage: ```main.py [-h] [-u URL] [-o OUTPUT] [-c CHAPTERS] [-i INITIALCHAPTER] [-l]```

optional arguments:
```
  -h,                                  Show this help message and exit
     --help
  -u URL,                              Url of any page within a chapter
     --url URL
  -o OUTPUT,                           Archive output
     --output OUTPUT           
  -c CHAPTERS,                         How many chapters should be downloaded
     --chapters CHAPTERS     
  -i INITIALCHAPTER,                   Initial number for Chapter sequence
     --initialchapter INITIALCHAPTER
  -l,                                  Use previous option
     --load
```

If there is only one chapter, it will be downloaded as single zip folder with the specified output name
If there are multiple chapters, it will download each chapter as a zip folder with the name of ch x.cbz, 
and then create a zip of chapter zips + comics.txt to create a [.cbc] (http://manual.calibre-ebook.com/conversion.html#comic-book-collections)
zip format. If you don not want to use .cbc, you can extract individual chapter zip from the .cbc zip file.


## Sample usage
```python main.py -c 9 -i 120 -o /tmp/Yamada\ XV.cbc -u http://www.mangahere.co/manga/yamada_kun_to_7_nin_no_majo/c120/```
