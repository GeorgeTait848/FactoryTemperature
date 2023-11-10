def signChange(a: float, b: float): 
    return (a <= 0 and b >=0) or (a >= 0 and b<=0)
    #only used for sinusoid so dont need to worry about point of inflection where this would give a false positive

def indexOfSignChangeIn(arr: list[float]): 

    for i in range(len(arr) - 1): 
        if signChange(arr[i], arr[i+1]): 
            return i+1

    return -1


def main():

    arr = [1,2,3,4,5,6,7,8,9,-1]
    print(indexOfSignChangeIn(arr))




if __name__ == "__main__":
    main()

