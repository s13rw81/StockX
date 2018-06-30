import numpy
def d2f(prices, dates):
    prices = numpy.round_(prices, 4)

    file1 = open('f_p.txt', 'w')
    
    for p in prices:
        file1.write(str(p))
        file1.write('\n')
    file2 = open('f_d.txt', 'w')
    
    for d in dates:
        file2.write(str(d))
        file2.write('\n')
    
    file1.close()
    file2.close()