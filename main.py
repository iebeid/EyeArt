import numpy as np

def main():
    coords = np.mgrid[0:1:100j]
    print(coords)

if __name__ == '__main__':
    main()