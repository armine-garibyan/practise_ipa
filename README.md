# Practise IPA
#### Video Demo:  <URL HERE>
#### Description:

*Practise IPA* is aimed at first year students majoring in English. It does not attempt to cover Engilsh varieties comprehensively, but only serves to provide IPA practice as the name suggests.

#### Features:

- **Progressive Difficulty Levels**: *Practise IPA* offers three distinct levels of difficulty. Choose between Levels 1, 2 and 3, each presenting varying degrees of mismatch between phonemes and graphemes.
- **Large Word Database**: Practice with real and relevant vocabulary. *Practise IPA* generates random words based on your selected difficulty level, providing you with a diverse range of transcription challenges. At the moment, the database include 5000 most frequent words from the *BNC*.
- **Instant Feedback**: After submitting your transcription attempt, *Practise IPA* provides instant feedback. It assesses the accuracy of your transcription and offers the correct IPA representation, helping you learn from your mistakes.
- **British English Support** (with More to Come): Currently, *Practise IPA* focuses on British English RP phonemes, with target transcriptions based on the *OALD*. In the future, an American English interface will be added.

If you want your training data to be used for research purposes (e.g., to see how effective the app is), please create an account. Email information will not be collected (only username and password). 

Below is a more detailed description of the project as well as individual files for the Harvard CS50 class.

-----------------------------

The main `app.py` file contains imports as well as declarations of the Flask instance, SQLite database and multile routes.

The `index` route is the homepage that leads to the `levels` route where users can choose the level of difficulty for practice. Once the level is chosen, users land on either `level_1`, `level_2` or `level_3` route. The corresponding templates are identical.
The difference is achieved through splitting the 5000 words in the `phon_br.csv` into 3 groups. The split is handled in the `app.py` file.

Each of the templates representing one of the levels features the IPA phonemes with example words (drawn from the `sounds.csv`) on the left as well as the practice tool on the right.
The practice tool represents a combination of input fields and buttons. Their behaviour is handled by JavaScript in the respective templates.

The applications also has a registration and a login functions which are handled by `register` route. Once a user registers successfully, `registered` template is rendered. Although login is not required for any of the routes, the user can do so voluntarily if they allow for their training data to be collected.
Data collection has not been implemented yet.
