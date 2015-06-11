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
<br>1) Numpy (http://www.numpy.org/)
<br>2) XlsxWriter (https://xlsxwriter.readthedocs.org/)

See some explanations about this software (in french):<br>
http://trajectoire-predict.monsite-orange.fr/

Limitations : <br>
1) only flights with departure and arrival airports are managed, hence inbounds or outbounds are not yet implemented <br>
2) the arrival and the departure airport needs to have each a runway defined in the runways database

A typical flight plan reads as follows:<br>
ADEP/LFST/23-POGOL-DANAR-RESPO-DIJON-PIBAT-MOULINS-KUKOR-LARON-GUERE-BEBIX-LIMOGES-ADES/LFBD/11<br>
where ADEP is the departure airport and ADES the destination, 23 being the departure runway and 11 the arrival runway.


