/*
 * Gerador de pi
 * Aritmética de precisão arbitrária implementada direto
 * Fórmula de Machin: π = 4×(4×arctan(1/5) - arctan(1/239))
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/*
 * Aritmética de precisão arbitrária usando base 10000.
 * Cada "dígito" é um int de 0-9999, representando 4 dígitos decimais.
 */

static int NBLOCKS = 0;

typedef struct {
    int *d;    /* blocos base 10000, d[0] = mais significativo */
    int n;     /* número de blocos */
} BigInt;

static BigInt* bi_new(void) {
    BigInt *b = (BigInt*)malloc(sizeof(BigInt));
    b->n = NBLOCKS;
    b->d = (int*)calloc(NBLOCKS, sizeof(int));
    return b;
}

static void bi_free(BigInt *b) {
    if (b) { free(b->d); free(b); }
}

static void bi_copy(BigInt *dst, BigInt *src) {
    memcpy(dst->d, src->d, NBLOCKS * sizeof(int));
}

static void bi_set_int(BigInt *b, int val) {
    memset(b->d, 0, NBLOCKS * sizeof(int));
    b->d[0] = val;
}

/* b = b / divisor (small int), retorna resto */
static int bi_div_small(BigInt *b, int divisor) {
    long long carry = 0;
    for (int i = 0; i < NBLOCKS; i++) {
        long long cur = carry * 10000LL + (long long)b->d[i];
        b->d[i] = (int)(cur / divisor);
        carry = cur % divisor;
    }
    return (int)carry;
}

/* b = b * mult (small int) */
static void bi_mul_small(BigInt *b, int mult) {
    long long carry = 0;
    for (int i = NBLOCKS - 1; i >= 0; i--) {
        long long cur = (long long)b->d[i] * mult + carry;
        b->d[i] = (int)(cur % 10000);
        carry = cur / 10000;
    }
}

/* dst += src */
static void bi_add(BigInt *dst, BigInt *src) {
    int carry = 0;
    for (int i = NBLOCKS - 1; i >= 0; i--) {
        int s = dst->d[i] + src->d[i] + carry;
        dst->d[i] = s % 10000;
        carry = s / 10000;
    }
}

/* dst -= src (assume dst >= src) */
static void bi_sub(BigInt *dst, BigInt *src) {
    int borrow = 0;
    for (int i = NBLOCKS - 1; i >= 0; i--) {
        int s = dst->d[i] - src->d[i] - borrow;
        if (s < 0) { s += 10000; borrow = 1; }
        else { borrow = 0; }
        dst->d[i] = s;
    }
}

/* verifica se b é zero */
static int bi_is_zero(BigInt *b) {
    for (int i = 0; i < NBLOCKS; i++)
        if (b->d[i] != 0) return 0;
    return 1;
}

/*
 * arctan(1/x) usando série de Taylor:
 * arctan(1/x) = 1/x - 1/(3x³) + 1/(5x⁵) - ...
 *
 * Trabalha com BigInt representando o valor × 10^precisão
 */
static void arctan_inv(BigInt *result, int x) {
    BigInt *power = bi_new();
    BigInt *term = bi_new();

    /* power = 1 (em precisão) */
    bi_set_int(power, 1);

    /* power = power / x (= 1/x) */
    bi_div_small(power, x);

    int x_sq = x * x;

    /* result = 0 */
    memset(result->d, 0, NBLOCKS * sizeof(int));

    for (int k = 0; ; k++) {
        int den = 2 * k + 1;

        /* term = power / den */
        bi_copy(term, power);
        bi_div_small(term, den);

        if (bi_is_zero(term)) break;

        if (k % 2 == 0) {
            bi_add(result, term);
        } else {
            bi_sub(result, term);
        }

        /* power = power / x² */
        bi_div_small(power, x_sq);
    }

    bi_free(power);
    bi_free(term);
}

/* ========================================= */
/* Interface exportada                        */
/* ========================================= */

static char *PI_DIGITS = NULL;
static long PI_COUNT = 0;
static int PI_READY = 0;

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __attribute__((visibility("default")))
#endif

EXPORT int pi_calcular(long n_digitos) {
    if (PI_READY && PI_COUNT >= n_digitos) return 0;

    /* cada bloco = 4 dígitos decimais */
    NBLOCKS = (int)(n_digitos / 4) + 10;

    fprintf(stderr, "Calculando %ld digitos de pi (%d blocos)...\n",
            n_digitos, NBLOCKS);

    clock_t t0 = clock();

    BigInt *at5 = bi_new();
    BigInt *at239 = bi_new();
    BigInt *pi = bi_new();

    fprintf(stderr, "  arctan(1/5)...\n");
    arctan_inv(at5, 5);

    fprintf(stderr, "  arctan(1/239)...\n");
    arctan_inv(at239, 239);

    /* pi = 4 × (4×arctan(1/5) - arctan(1/239)) */
    bi_mul_small(at5, 16);   /* 4 × 4 */
    bi_mul_small(at239, 4);  /* 4 × 1 */

    bi_copy(pi, at5);
    bi_sub(pi, at239);

    /* extrair dígitos */
    if (PI_DIGITS) free(PI_DIGITS);
    PI_DIGITS = (char*)malloc(n_digitos + 100);

    long pos = 0;
    for (int i = 0; i < NBLOCKS && pos < n_digitos; i++) {
        char buf[8];
        if (i == 0) {
            sprintf(buf, "%d", pi->d[i]);
        } else {
            sprintf(buf, "%04d", pi->d[i]);
        }
        for (int j = 0; buf[j] && pos < n_digitos; j++) {
            PI_DIGITS[pos++] = buf[j];
        }
    }
    PI_DIGITS[pos] = '\0';
    PI_COUNT = pos;
    PI_READY = 1;

    bi_free(at5);
    bi_free(at239);
    bi_free(pi);

    double elapsed = (double)(clock() - t0) / CLOCKS_PER_SEC;
    fprintf(stderr, "Pronto: %ld digitos em %.1f segundos.\n", PI_COUNT, elapsed);
    fprintf(stderr, "Verificacao: %.20s...\n", PI_DIGITS);

    return 0;
}

EXPORT int pi_digito(long pos) {
    if (!PI_READY || pos < 0 || pos >= PI_COUNT) return 0;
    return PI_DIGITS[pos] - '0';
}

EXPORT long pi_total(void) {
    return PI_COUNT;
}

EXPORT void pi_liberar(void) {
    if (PI_DIGITS) { free(PI_DIGITS); PI_DIGITS = NULL; }
    PI_COUNT = 0;
    PI_READY = 0;
}