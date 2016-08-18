
def numbTrans(n):
    import re
    import numpy as np
    aant = n.str.split('AANT.|AANT', expand=True)[1]
    aantRe = re.compile(r'\d+')
    results = []
    count = 0
    for i in aant:
        try:
            i = aantRe.search(i).group()
            results.append(i)
            aant[count] = i
            count+=1
        except:
            i = None
            count+=1

    n = aant.astype('float')
    n = np.where(n.isnull(), 1, aant)



    return (n)
