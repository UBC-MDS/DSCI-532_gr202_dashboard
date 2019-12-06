### What the dashboard does well
- The app is aesthetically pleasing. Matching colour scheme across the dropdown menus, sliders and the plots themselves. Unique visualizations such as the choropleth of Boston and heatmap are visually pleasing and informative. The app layout allows the user to see every single plot at the same time, but also it gives the user access to the dropdown menus while being able to see every single plot. That way the user can instantly see the change in each plot, a filter is applied.  
- The app incorporates a wide range of different visualizations in order to deliver a wide range of information regarding crime in Boston. 
- It gives the user a variety of ways to filter and select the dataset, with sliders and dropdown menus. It gives the user a lot of options to see which portion of the data are most relevant for each user. 
- The app is responsive to the sliders and dropdown menus. Every graph updates in order to display the user’s selected options. The graphs updates very quickly to change in user options.
  
### Critiques and Future Improvements 
- It loads too slowly on Heroku. It takes over 10 seconds to load every single plot. A potential improvement is to subset the dataset, so we don’t have to load the entire dataset. Another solution is to make tabs to house different plots, so all four plots aren’t displayed on the same page.
  - The app loads very quickly locally when altair's data server is enabled with `alt.data_transformers.enable('data_server')`. However, this functionality does not work with Heroku as per our [discussion](https://github.com/altair-viz/altair_data_server/issues/11) with the creator of this function.
- On a smaller display 13”, the plots can’t be fully displayed, the user has to horizontally scroll the plot in order to see the entire content of the plot. A potential solution for this is to have tabs to house different plots. 
- A potential future addition is to include more plots. In addition, to categorize the plots, so similar plots can be placed together. For instance, plots relating to when crimes occurs (time of date, month and etc) can be put into a tab by itself. While plots relating to where crimes occurs can be put into another tab. This might help the user digest the information provided to them easier. In addition, it might help speed up load time. 

### Github Issues
<<<<<<< HEAD
- Teammate Issues 
  - Whenever a team member spotted a bug or issue related to the app, they created a GitHub issue. A succinct and descriptive message regarding the problem is written. In which, other team members can attempt to fix the problem. After the problem is fixed, the specific commit was referenced to that issue. 
- TA Issues
  - Teamwork contract have been updated in individual repo to be more specific as per request of TA.
  - [Proposal](https://github.com/UBC-MDS/DSCI-532_gr202_dashboard/blob/master/Proposal.md) have been updated to reference count instead of density and count instead of rates. 
=======
- Team Issue
  - Whenever a team member spotted a bug or issue related to the app, they created a GitHub issue. A succinct and descriptive message regarding the problem was written. In which, other team members attempted to fix the problem. After the problem was fixed, the specific commit was referenced to that issue. 
- TA Issues
  - Fixed references of 'density' to 'count' and 'rates' to 'count' in proposal and REAMDE to reflect updated project scope.
  - Updated Team Contract in personal repos, to be more specific about division of work and deadlines. 



>>>>>>> upstream/master
