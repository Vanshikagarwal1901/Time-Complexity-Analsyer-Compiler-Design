#include <stdio.h>

int main() {
    int n = 1000;
    int sum = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 1; j < n; j *= 2) {
            sum += i + j;
        }
    }
    printf("%d\n", sum);
    return 0;
}
