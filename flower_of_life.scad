radius=60;

difference() {
    circle($fa=3,r=(3*radius)+3);
    circle($fa=3,r=(3*radius));
};

petal_pattern();
rotate([0,0,60])
        petal_pattern();
rotate([0,0,120])
        petal_pattern();

module petal_pattern(){

    for (i = [-3:1:2]) {
        petal(0, i);
    };
    for (i = [-2.5:1:1.5]) {
        petal(1, i);
    };
    for (i = [-2:1:1]) {
        petal(2, i);
    };
    for (i = [-1.5:1:0.5]) {
        petal(3, i);
        };
    for (i = [-2.5:1:1.5]) {
        petal(-1, i);
    };
    for (i = [-2:1:1]) {
        petal(-2, i);
    };
    for (i = [-1.5:1:0.5]) {
        petal(-3, i);
    };
};
module petal(petal_x_offset=0, petal_y_offset=0){   

        //echo([petal_y_offset]);
        
        translate([petal_x_offset*(radius/2)*sqrt(3), petal_y_offset*radius, 0])
        intersection() {
                translate([(radius/2)*sqrt(3), radius/2, 0])
                    circle($fa=5,r=radius);
                translate([-(radius/2)*sqrt(3), radius/2, 0])
                circle($fa=5,r=radius);
        }
};
