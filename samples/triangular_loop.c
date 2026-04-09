#include <stdio.h>

int main() {
    int n = 1000;
    int sum = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < i; j++) {
            sum += j;
        }
    }
    printf("%d\n", sum);
    return 0;
}
