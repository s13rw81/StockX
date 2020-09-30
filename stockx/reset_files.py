#this module clears the txt files
def vanish():
    p0 = open("b_s_p.txt","w")
    p1 = open("b_s_d.txt","w")
    p0.close()
    p1.close()
    p3 = open("f_p.txt","w")
    p4 = open("f_d.txt","w")
    p3.close()
    p4.close()
    p5 = open("linegraph.txt", 'w')
    p5.close()
    print('File contents cleared.')