## Summary

A traffic simulation program that graphically depicts automobile traffic on real world road systems. 

Currently the program supports the following feature set:
- Taking dynamic real world map data (from OpenStreetMaps) and creating a graph of vertices and edges.
- Creating a visual representation of the internal graph by drawing a map using only lines and circles.
- Adding car objects can drive along the map and randomly pick destinations to travel to with routes.
- Optimal route determination using Dijkstra's search algorithm.
- Cars that will obey one way roads, speed limits, and will attempt to avoid collisions with one another. 
- Collision detection optimization through the use of a quad tree.

## Version

Developed in Python 3.6.5

## Instructions
1) install Python 3.6 or later
2) install PyYAML -> `pip install PyYAML`
3) install overpy -> `pip install overpy`
4) run `main.py` from command line -> `python main.py`

## Demo
![Demo](https://github.com/andrewlavaia/Traffic-Simulation/blob/master/demo.gif?raw=true)

## Python Third Party Modules

- PyYAML -> pip install PyYAML
- overpy -> pip install overpy

## References

- Algorithms - Robert Sedgewick and Kevin Wayne (Fourth Edition, 2011)
- OpenStreetMaps - all map data is provided through the OpenStreetMaps Overpass API
- US Census - Zip Code Tabulation Areas (https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html)

## License

MIT 