# Web-Dashboard

![image](/images/Dashboard.jpg)

### Description
This web dashboard and utilizes Plotly Dash and PyMongo to interact with a MongoDB database containing information about shelter animals in the Austin Texas area. The Dashboard incorporates a table, a map, a graph, and dropdown menus. The menus execute different MongoDB queries depending on what is selected and return the corresponding animal data. The animal data is then displayed in the table with the locations of each animal plotted on the map.

### Why I selected this item
This project is a practical example of how databases can be used in a web-based dashboard. To facilitate the interaction of the dashboard with the database, a custom Python module was created with methods that perform typical CRUD operations (create, read, update, and delete). These methods authenticate the user, load the database, and return query results to the main program.

To improve the dashboard, several changes were made. First, I generalized the filtering options by incorporating multiple dropdown menus for selecting different animal characteristics. I created menus for the animal type, breed, and gender as well as a slider element for specifying an age range. When the user selects an option from one of the menus, all of the other menus automatically update to show only options that are consistent with the first selection. For example, if a cat is selected for animal type, then the breeds menu will only show cat breeds. 

### Course Objectives
I exceeded course objectives with this project by greatly improving the functionality of the dashboard with dynamic dropdown menus and a slider. In addition to the new menus, I updated the appearance of the dashboard to give it a more modern look. I improved the python code by removing redundancies and by incorporating descriptive comments.

### Reflection
While enhancing the program, I learned several new things like how to dynamically populate the menus using a callback method. When a menu option is selected, the callback queries the database for the selection. The unique values for animal type, breed, and gender are then extracted using the Pandas module’s unique() method and returned to update the menus. I also learned how to improve the layout of the dashboard using relative scaling based on the screen size and using a .css file to change the appearance of various components. Modifying the appearance of the dashboard challenging as it not intuitive how to customize each of the components. Some components like the table have many controls for changing how they look and behave, but other components like the dropdown menus have relatively few controls. The CSS file allows for additional customization not inherent to dash elements. 
