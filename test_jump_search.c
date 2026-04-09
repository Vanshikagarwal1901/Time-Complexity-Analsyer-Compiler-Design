#include <stdio.h>
#include <math.h>

int jumpSearch(int arr[], int n, int x) {
    int step = (int)sqrt(n);
    int prev = 0;
    while (arr[step - 1] < x) {
        prev = step;
        step += (int)sqrt(n);
        if (prev >= n) return -1;
    }
    while (arr[prev] < x) {
        prev++;
        if (prev == step || prev == n)
            return -1;
    }
    if (arr[prev] == x) return prev;
    return -1;
}

int main() {
    int arr[] = {0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89};
    int n = 12;
    int x = 55;
    int index = jumpSearch(arr, n, x);
    printf("Element found at index: %d\n", index);
    return 0;
}
