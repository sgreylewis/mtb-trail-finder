# Shred-Head: A Mountain Bike Trail Recommender

## Motivation

As a mountain biker, whether you’ve been riding for years or just starting out,
you’re always looking for the next trail to shred.  It’s easiest to get recommendations from other riders in the parking lot of your favorite trail, but you can also ask around at local bike shops, Facebook or Meetup groups for mountain bikers, and websites such as [Trail Forks](https://www.trailforks.com) and [MTBProject](https://www.mtbproject.com).  Still, when being told that a ride unknown to you is “totally epic”, you wonder, “Will it be fast and flowy or more rocky and technical?  Are there lots of drops and if so, can I roll them?  Is it mostly climbing, descending, or an equal amount of both? Is it an out and back, loop, lollipop, or do I need a shuttle? If it’s going to be a long day in the saddle, are there bailouts just in case?”  MTBProject.com and Trailforks.com do a good job of answering these questions for you when you search for the stats of a specific trail, but wouldn’t it be nice if you could get a recommendation based on the trails you know and like?  Or if you know you want a new ride that’s a certain length, within a certain distance of where you are, and a certain level of technicality, what should you ride?  Whether you’ve ridden all the trails in your area and are looking for a new one, or are headed to Durango for a weekend and looking for some downhill shuttled rides, Shred-Head has the perfect ride tailored to your desires.

## Data

I wrote python code that made enough requests to [MTB Project's API](https://www.mtbproject.com//data) to get
data on 26,752 trails in all 50 states and the nation's capital.  The API data came
in JSON files, which were very easy to access and concat.  The raw features were:
['ascent', 'conditionDate', 'conditionDetails', 'conditionStatus', 'descent', 'difficulty','high', 'id', 'imgMedium', 'imgSmall', 'imgSmallMed', 'imgSqSmall', 'latitude', 'length', 'location', 'longitude', 'low', 'name', 'starVotes', 'stars', 'summary', 'type', 'url'].  

## Feature Engineering

Since I want to build a content-recommender that will compare trails on their features, I dropped ['conditionDate', 'conditionDetails', 'conditionStatus','high', 'id', 'imgMedium', 'imgSmall', 'imgSmallMed', 'imgSqSmall', 'low', 'starVotes'] since I didn't believe those features, even the images, are the best indicators of what makes trails similar.  I didn't end up using all the remaining features, such as 'latitude', 'longitude', 'summary', and 'url', to make my comparisons but I kept them as I would need them in my website; I also created a few new columns for 'city/town' and 'state' so that I could later search the trails by state and/or location.  I found 5,804 trails were of the type 'Connector', which is a trail that is most likely less than 1 mile long and intended as a bypass or connection between trails or trail systems; therefore I didn't think it desirable to recommend them as trails to ride on.  I also dropped the 37 trails that had missing difficulty ratings, as this would be an attribute I would use for comparison of trails.  Knowing that riders would prefer to see a set of trails with a specific range of distances, I created a length_range column that categorized each trail within a certain distance range.  In order to make the comparisons, I needed to quantify all features that I planned to use so I encoded 'difficulty', and created dummy variable columns for 'type'.  Lastly, I cleaned up columns with string values to make them more presentable for visualizations and the website.  

## Exploratory Data Analysis through Visualizations and Maps
