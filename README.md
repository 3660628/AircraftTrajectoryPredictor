# AircraftTrajectoryPredictor
<h2> Purpose </h2>
To compute a Jet Aircraft trajectory prediction based upon BADA<br>
https://www.eurocontrol.int/services/bada

<h2> Langage </h2>
This software is written in Python 2.7.<br>
https://www.python.org/

<h2> Outputs </h2>
It allows to compute aircraft (jet) trajectories. 
Three kind of outputs are generated: 
<br>1) a Google Earth KML file
<br>2) and two xlsx containing the vertical flight profile and the lateral profile.
<br>

<h2> Inputs - Data Inputs </h2>
<br> 1) a Way Point database
<br> 2) a Run Way database
<br> 3) an Airport database

<h2> Pre Requesites </h2>
This software needs :
<br>1) Numpy (http://www.numpy.org/)
<br>2) XlsxWriter (https://xlsxwriter.readthedocs.org/)

<h2> Web Page </h2>
See some explanations about this software (in french):<br>
http://trajectoire-predict.monsite-orange.fr/

<h2> Restrictions and Limitations </h2>
1) only flights with departure and arrival airports are managed, hence inbounds or outbounds are not yet implemented <br>
2) the arrival and the departure airport needs to have each a runway defined in the runways database

<h3> Flight Plan </h3>
A typical flight plan reads as follows:<br>
ADEP/LFST/23-POGOL-DANAR-RESPO-DIJON-PIBAT-MOULINS-KUKOR-LARON-GUERE-BEBIX-LIMOGES-ADES/LFBD/11<br>
where ADEP is the departure airport and ADES the destination, 23 being the departure runway and 11 the arrival runway.


