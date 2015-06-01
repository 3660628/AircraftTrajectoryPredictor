# AircraftTrajectoryPredictor
Jet Aircraft Trajectory Prediction based upon BADA

Aircraft trajectory prediction based upon BADA<br>
https://www.eurocontrol.int/services/bada

This software is written in Python 2.7.<br>
https://www.python.org/

It allows to compute aircraft (jet) trajectories. 
Three kind of outputs are generated. 
A Google Earth KML file and two xlsx containing the vertical flight profile and the lateral profile. 
This software needs :
<br>-1) Numpy (http://www.numpy.org/)
<br>-2) XlsxWriter (https://xlsxwriter.readthedocs.org/)

See some explanations about this software (in french):<br>
http://trajectoire-predict.monsite-orange.fr/

Limitations : 
1) only flights with departure and arrival airports are manage, hence inbounds or outbounds not yet implemented
2) the arrival and the departure airport needs to have each a runway defined in the runways database

