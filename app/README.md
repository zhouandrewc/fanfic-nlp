# "Yip Yip!": An Interactive Fanfiction App
## by Andrew Zhou

An application with 3 components.

* A fanfiction recommender: recommends <em>Avatar: The Last Airbender</em> fanfiction from my assembled corpus, given input fanfiction text from a user.
* A fanfiction generator: generates text in the style of <em>Avatar: The Last Airbender</em> fanfiction.
* A fanfiction analyzer: given the text of an <em>Avatar: The Last Airbender</em> fanfiction, calculates character and pairing frequencies and plots them on an interactive chord diagram.


### Tools Used

* [WordCloud](https://amueller.github.io/word_cloud/)
* Streamlit
* Flask
* d3
* HuggingFace
* PyTorch
* Gensim

### Data

Our data are from the website [Archive of Our Own](http://archiveofourown.org), or AO3.

## Notes

The app is currently not deployed (10 December 2020) but I'm working on doing so; I want to clean up the functionality and to ensure that rehosting short snippets of text from AO3 users' fanfictions is permissible. Screenshots and ```.gif```s of the app may be found in the [```examples```](examples) folder.

The text used for the recommender example is taken from the fanfiction [Salvage](https://archiveofourown.org/works/21116591/chapters/50249441) and the text for the analyzer example is taken from the fanfiction [Icarus, Point to the Sun](https://archiveofourown.org/works/27089068).