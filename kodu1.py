from statistics import mean
# import matplotlib.pyplot as plt
def silu_andmed(a,n):
    fail=open(a)
    f=fail.readlines()
    b=[]
    kesk=[]
    kesk2=[]
    rida=[i.strip().split(",") for i in f]
    for i in rida:
        b.append(i[1])
    c=[float(i) for i in b]
    for i in c:
        kesk.append(i)
        if len(kesk)>n:
            keskmine=[mean(kesk[-51:-1])]
            kesk2.append(keskmine)
        else:
            keskmine=[mean(kesk)]
            kesk2.append(keskmine)
    fail.close()
#    plt.plot(c)
#    plt.plot(kesk2)
#    plt.ylabel(kesk2)
#   plt.show()
