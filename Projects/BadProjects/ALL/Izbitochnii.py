import math

max_Stepper1_pos = 3756
max_Stepper2_pos = 800
max_Stepper3_pos = 612

max_angle1 = 135*2
max_angle2 = 90*2
max_angle3 = 90*2

middle1 = max_Stepper1_pos//2
point1 = max_Stepper1_pos//max_angle1

middle2 = max_Stepper2_pos//2
point2 = max_Stepper2_pos//max_angle2

middle3 = max_Stepper3_pos//2
point3 = max_Stepper3_pos//max_angle3


def CALCULATOR_LENIVOGO_ARTEMA(angle):
    if angle[0] > 130:
        angle[0] = 130
    if angle[1] > 85:
        angle[1] = 85
    if angle[2] > 85:
        angle[2] = 85

    if angle[0] < -130:
        angle[0] = -130
    if angle[1] < -85:
        angle[1] = -85
    if angle[2] < -85:
        angle[2] = -85

    position1 = int(middle1+angle[0]*point1)
    position2 = int(middle2-angle[1]*point2)
    position3 = int(middle3-angle[2]*point3)
    
    return(position1, position2, position3)
    
