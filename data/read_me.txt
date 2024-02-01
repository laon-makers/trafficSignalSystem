
err_route_1.txt: It seems to be caused by missing fork tine information. 
                 The horizontal TS I4 has 2 junctions but only one paire of tines for the junction
                 on the left is available with current design as of May 21, 2023.
                 Therefore the routing algorithm for the reveser direction train #2 didn't work.
                 It was refering to wrong tines when it calcurate train #2's routing path.