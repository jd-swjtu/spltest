# spltest
Install below packages
```
    pip install requests
    pip install pytest
```

Run script
```
    git clone https://github.com/jd-swjtu/spltest.git
    cd spltest
    
    pytest -s spltests.py

    #You will see logs are printed on stdout, or you can check logs in test.log at current folder
```


Test Cases:
* TC1: Call GET movies with name which inclues empty, blanks, special chars, Chinese chars, UTF-8 encoding, unicode encoding
* TC2: Call GET movies without count, with count=0, count=big number, count=negative number, count=other string
* TC3: Call GET movies with head 'Accept: Application/json', or 'Accept: application/json' or others 'Accept: */*' or without 'Accept' head
* TC4: Call POST movies with name and description with validate words
* TC5: Call POST movies with name and description with validate words, with head 'Content-Type: application/json', 'Accept: */*'
* TC6: Call POST movies with name and description which are empty, blanks, special chars, Chineese chars, UTF-8, unicode encoding
* TC7: Call POST movies with invalid JSON string
* TC8: Call POST movies with other fields besides name and description
* TC9: Call POST movies with name which is number, boolean, json array, json object
* TC10: Call GET movies, make sure there should no two movies hasve the same 'poster_path'
* TC11: Call GET movies, validate the poster_path can be null, empty(not present), or validte url address(https://..., http://..., or relative path)
* TC12: Call GET movies, validate the movies with genre_ids == null should be first in response, and sorted by id(ascending); for movies with non-null genre_ids, the results should be sorted by id(ascending)
* TC13: Call GET movies, validate the number of movies whose sum of 'genre_ids' > 400 should be no more than 7. (Need preprare data and combined the query with count)
* TC14: Call GET movies, validate there is one movie whose title has a palindrome word in it
* TC15: Call GET movies, validate there are at least two movies whose title contain the title of anothere movie

Bugs:
* Above test cases failed except TC4, TC13, TC14
