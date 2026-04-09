#include <stdio.h>

int main() {
    int n;
    scanf("%d", &n);

    for (int i = 2; i <= n; i = i * i) {          // Loop 1
        for (int j = 1; j * j <= i; j++) {        // Loop 2
            for (int k = j; k > 0; k = k / 2) {   // Loop 3
                printf("*");
            }
        }
    }
    return 0;
}
