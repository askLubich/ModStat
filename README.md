# ModStat

Statistics about the user and moderator activity of [the subreddit /r/de](https://www.reddit.com/r/de/).

### Results

![alt text](sstat.png "stat summary")

Most of the categories are pretty self explanatory. However, a couple of additional pieces
of information might me helpful:

* Each time a post/comment is reported by a user or filtered by a bot, a moderator needs to make an approve/remove devision.

* "approved reported/filtered posts" shows the number of posts that have been approved by a moderator after being reported or filtered.

* The same goes for removed posts and approved/removed comments respectively.

* Therefore, the data about posts and comments does *not* reflect the total number of posts and comments, put only those that were reported or filtered. This is only a small subset.

* The stacked distribution shows the amount of specific mod actions relative to the total number of actions usind the same color coding as in the rest of the visualization. The difference to 1 is made up of other mod actions (like setting sticky posts, unbanning, assigning flair), which are not explicitly listed here.

* Unfortunately, I didn't save the data between 06.17 and 01.18 at the time and reddit does not allow accessing data that is older then 4 months. 

### Prerequisites

* Python 2.7
* Jupyter Notebook
* Packages:
    * matplotlib
    * numpy
    * sys

### Raw Data

The raw data is contained in files named using the pattern "YYMM.csv". For instance "1610.csv" contains the data for October 2016. 
The csv-files were downloaded from the moderation log using the moderation log matrix framework, supplied by the [reddit mod toolbox](https://www.reddit.com/r/toolbox/).
Original files are not included for privacy reasons, since they contain the activity profiles of each moderator during each month.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.