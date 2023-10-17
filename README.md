# salesforcePython
A Salesforce integration using python

__1__- Make sure to change login_params! <br>
__2__- tqdm was not mandatory for the function get_table() to run, but it was quite useful when loading giant objects such as "fact tables". <br>
__3__- I did not have a test user I could implement into this code (I'll try and come up with something to solve this), but the objects I used to implement were default objects from Salesforce and they might be the same for everyone.<br> 
__4__- When using get_query() try using double cotes or docstring, since simple cote might be required in your query for strings.<br>
  _e.g.:_ <br><br>
  [in:] __get_query("SELECT col1, col2 FROM tb1 WHERE col2 LIKE '%substring%' ORDER BY col1")__<br>__get_query(query)__<br><br>
  or,<br>
  [in:] __query = '''__<br>
                __SELECT col1, col2__<br>
                __FROM tb1__<br>
                __WHERE col2 LIKE '%substring%'__<br>
                __ORDER BY col1__<br>
              __'''__<br>__get_query(query)__<br><br>
__5__- SOQL syntax and functions can be found here: https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm<br>
__6__ - __How to Generate a Security Token in Salesforce:__
* Log in to your Salesforce account. ...
* Click the profile avatar and choose Settings.
* Select My Personal Information → Reset My Security Token.
* Check your email for the security token.
