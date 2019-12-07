## Reflections for Milestone 2
### What the dashboard does well
- The app is aesthetically pleasing. Matching colour scheme across the dropdown menus, sliders and the plots themselves. Unique visualizations such as the choropleth of Boston and heatmap are visually pleasing and informative. The app layout allows the user to see every single plot at the same time, but also it gives the user access to the dropdown menus while being able to see every single plot. That way the user can instantly see the change in each plot, a filter is applied.  
- The app incorporates a wide range of different visualizations in order to deliver a wide range of information regarding crime in Boston. 
- It gives the user a variety of ways to filter and select the dataset, with sliders and dropdown menus. It gives the user a lot of options to see which portion of the data are most relevant for each user. 
- The app is responsive to the sliders and dropdown menus. Every graph updates in order to display the user’s selected options. The graphs updates very quickly to change in user options.
  
### Critiques and Future Improvements 
- It loads too slowly on Heroku. It takes over 10 seconds to load every single plot. A potential improvement is to subset the dataset, so we don’t have to load the entire dataset. Another solution is to make tabs to house different plots, so all four plots aren’t displayed on the same page.
  - The app loads very quickly locally when altair's data server is enabled with `alt.data_transformers.enable('data_server')`. However, this functionality does not work with Heroku as per our [discussion](https://github.com/altair-viz/altair_data_server/issues/11) with the creator of this function.
- On a smaller display 13”, the plots can’t be fully displayed, the user has to horizontally scroll the plot in order to see the entire content of the plot. A potential solution for this is to have tabs to house different plots. 
- A potential future addition is to include more plots. In addition, to categorize the plots, so similar plots can be placed together. For instance, plots relating to when crimes occur (time of date, month and etc) can be put into a tab by itself. While plots relating to where crimes occur can be put into another tab. This might help the user digest the information provided to them easier. In addition, it might help speed up load time. 

### Github Issues
- Teammate Issues 
  - Whenever a team member spotted a bug or issue related to the app, they created a GitHub issue. A succinct and descriptive message regarding the problem is written. In which, other team members can attempt to fix the problem. After the problem is fixed, the specific commit was referenced to that issue. 
- TA Issues
  - Teamwork contract has been updated in the individual repo to be more specific as per the request of TA.
  - [Proposal](https://github.com/UBC-MDS/DSCI-532_gr202_dashboard/blob/master/Proposal.md) has been updated to reference count instead of density and count instead of rates. 

- Team Issue
  - Whenever a team member spotted a bug or issue related to the app, they created a GitHub issue. A succinct and descriptive message regarding the problem was written. In which, other team members attempted to fix the problem. After the problem was fixed, the specific commit was referenced to that issue. 
- TA Issues
  - Fixed references of 'density' to 'count' and 'rates' to 'count' in proposal and REAMDE to reflect updated project scope.
  - Updated Team Contract in personal repos, to be more specific about the division of work and deadlines. 
  
 
## Reflections for Milestone 3
### Peer Feedback and Updates to App
We received valuable information both from watching our peers interact with our app, and also from their helpful feedback.  Overall, users enjoyed our aesthetics and the functionality of the app, and for the most part used the app as we had intended. However, a few specific areas of improvement were noted, which we address below: 
- The major complaint with the app, which was consistent across all reviewers was that our app deployment on Heroku is very slow. We have documented this previously, and are unable to improve at this point, other than by greatly reducing the size of our dataset. However, based on the speed of our static ggplot objects we are hopeful that our implementation in Milestone 4 will be significantly faster.  
- Our largest structural change was to completely remove the `month` filter. Our intention was for users to only use the month filter if they were looking at a specific year. However, without directly telling users our intention, this feature was not used as intended by our peers. When this feature is misused, it can provide some potentially meaningless filters. For example, users may filter months on March-June, for years 2016-2018, which _does not_ give data for the time frame March 2016 - June 2018, but actually only returns data from March-June for these three years. For milestone 4 we will consider re-implementing the month filter with additional restrictions.

We have also made smaller stylistic changes as a direct result of specific peer feedback include:
- A hyperlink to our datasource has been added at the bottom of the app.
- A hyperlink to our Github repository has been at the bottom of the app so that users can interact with us and/or report issues or bugs.
- We have expanded our introductory blurb to provide more specific use cases of the app, and expand the narrative for the benefits of the app. 
- We have filtered out the first and last months from our dataframe, as upon inspection they were not full months and therefore were affecting the monthly trend plot. 

Some comments from our peers were directly in contradiction to other peers. For example, some people wish only the specific neighbourhood would display on the choropleth when selected, while others really liked that the other neighbourhoods would still be included. These stylistic differences are to be expected as individuals all have unique tastes, and you cannot please everyone. In the cases with contradicting feedback, we had a group discussion on whether or not to make an adjustment to our app. 

We found the peer feedback process very helpful, and will look to gather additional feedback from our peers before our milestone 4 submissions.

## Maintenance to App
Beyond implementing the above features to our app based on user feedback, we have also done significant refactoring of our code. We have reorganized our app, by abstracting function definitions out of our app.py file to a new separate functions.py helper file. Code hygiene has also been improved by adding detailed docstrings for all functions, and making our code 'Pythonic' when possible (for example, dictionary comprehensions for long dropdown menus). 

