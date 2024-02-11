from fasterdtw import fastdtw

def printMap(a,b,path):
    print(a)
    print(b)
    for p in path:
        print(a[p[0]], " ==> ", b[p[1]])
    print("")

a=["Acesta", "este", "un", "test"]
b=["Acesta", "este", "un", "test"]
path=fastdtw(a,b)
printMap(a,b,path)


a=["Acesta.este", "un", "test"]
b=["Acesta", ".", "este", "un", "test"]
path=fastdtw(a,b)
printMap(a,b,path)


a=["Acesta", ".", "este", "un", "test"]
b=["Acesta.este", "un", "test"]
path=fastdtw(a,b)
printMap(a,b,path)

a=["a"]
b=["Acesta", "este", "un", "test"]
path=fastdtw(a,b)
printMap(a,b,path)

a=["Acesta", "este", "un", "test"]
b=["a"]
path=fastdtw(a,b)
printMap(a,b,path)


a=[]
b=["Acesta", "este", "un", "test"]
path=fastdtw(a,b)
printMap(a,b,path)

a=["Acesta", "este", "un", "test"]
b=[]
path=fastdtw(a,b)
printMap(a,b,path)

a=["1", "2", "3", "4"]
b=["5", "6", "7", "8"]
path=fastdtw(a,b)
printMap(a,b,path)


a=["Acesta", "este", "un", "test.x"]
b=["Acesta", "este", "un", "test",".","x"]
path=fastdtw(a,b)
printMap(a,b,path)

a=["Acesta", "este", "un", "test",".","x"]
b=["Acesta", "este", "un", "test.x"]
path=fastdtw(a,b)
printMap(a,b,path)
