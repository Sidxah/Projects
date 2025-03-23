#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <limits.h>

// Fonction utilitaire pour obtenir le maximum de deux nombres.
int max(int a, int b) { return (a > b) ? a : b; }
int min(int a, int b) { return (a < b) ? a : b; }


// Définition de la structure pour les objets.
typedef struct {
    unsigned int weight;
    unsigned int value;
} Item;


// Variables globales pour l'algorithme de backtracking
// (ATTENTION: nous utilisons les variables globales dans cette version pour suivre le schéma vu en cours et en td)
Item* g_itmes;             // tableau d'objets
int g_n;                   // nombre d'objets
int g_W;            // capacité du sac
int g_bestValue = 0;       // meilleure valeur trouvée jusqu'à présent
int g_currentValue = 0;    // valeur courante du sac
int g_currentWeight = 0;   // poids courant du sac
int* dp;                   // tableau des poids minimales pour atteindre la valeur des objets

// Fonction pour calculer la borne sup: << the currentValue + la valeur de tous les objets restées>> 
// note: si (borneSup <= *best_value) alors ça ne sert a rien de continuer le travail sur la branche !!! 
int borne_sup(Item items[], int n, int idx, int currentValue) {
    int i, borne_sup = currentValue;
    for(i = idx ; i < n ; i++) {
        borne_sup += g_itmes[i].value;
    }
    return borne_sup;
}


// implémentation récursive de l'algorithme de backtracking 
void knapsackBT1(int idx) {
    // Si l'indice actuel est hors le tableau ou si le sac à dos est plein, mettre à jour bestValue si nécessaire
    if (idx == g_n || g_currentWeight == g_W) {
        g_bestValue = max(g_bestValue, g_currentValue);
        return;
    }

	int bsup = borne_sup(g_itmes, g_n, idx, g_currentValue);
    if (bsup <= g_bestValue) {
        return ;
    }
    // sauter l'objet courant
    knapsackBT1(idx + 1);

    // Inclure l'objet actuel s'il ne dépasse pas la capacité du sac à dos
    if (g_currentWeight + g_itmes[idx].weight <= g_W) {
        // Mettre à jour currentWeight et currentValue avant l'appel récursif
        g_currentWeight += g_itmes[idx].weight;
        g_currentValue += g_itmes[idx].value;

        knapsackBT1(idx + 1);

        // Annuler la décision d'inclure l'objet (backtracking)
        g_currentWeight -= g_itmes[idx].weight;
        g_currentValue -= g_itmes[idx].value;
    }
}



// Algorithme de backtracking sans variables globales
int knapsackBTUtil(Item items[], int n, int W, int idx, int currentValue, int *bestValue) {
    if (idx == n || W == 0) {
        if (currentValue > *bestValue)
            *bestValue = currentValue;
        return *bestValue;
    }

    int bsup = borne_sup(items, n, idx, currentValue);
    if (bsup <= *bestValue) {
        return *bestValue;
    }

    // Ne pas inclure l'objet idx
    knapsackBTUtil(items, n, W, idx + 1, currentValue, bestValue);

    // Inclure l'objet idx si le poids le permet
    if (items[idx].weight <= W) {
        knapsackBTUtil(items, n, W - items[idx].weight, idx + 1, currentValue + items[idx].value, bestValue);
    }

    return *bestValue;
}

int knapsackBT2(Item items[], int n, int W) {
    int bestValue = 0;
    return knapsackBTUtil(items, n, W, 0, 0, &bestValue);
}

/**** Exercice 05 :                         ****/
// Focntion qui retourne la somme des valeurs des objets dans le tableau tab
int getSommeValue(Item items[], int n) {
    int v = 0;
    for(int i = 0; i < n ; i++) {
        v += items[i].value;
    }
    return v;
}


void initialiserDP(Item items[], int * dp, int n) {
    dp[0] = 0;
    for(int i = 1; i < n ; i++) {
        dp[i] = __INT_MAX__;
    }
} 

int knapsackDP_Value(Item * items, int v, int i) {
    if (v == 0) return 0;
    return min(knapsackDP_Value(items, v - items[i].value, i-1), knapsackDP_Value(items, v, i-1));
}

void construireDP(Item * items, int * dp, int n) {
    int V = getSommeValue(items, n);
    initialiserDP(items, dp, V);
    int i;
    for(i = 0 ; i < V ; i++) {
        dp[i] = knapsackDP_Value(items, i, n);
    }
}



// Fonction de programmation dynamique pour le problème du sac à dos 0/1.
int knapsackDP(int W, Item items[], int n) {
    int i, w;
    int **K = (int**)malloc((n+1) * sizeof(int*));
    for(i = 0; i <= n; i++)
        K[i] = (int*)malloc((W+1) * sizeof(int));

    for(i = 0; i <= n; i++) {
        for (w = 0; w <= W; w++) {
            if (i == 0 || w == 0)
                K[i][w] = 0;
            else if (items[i-1].weight <= w)
                K[i][w] = max(items[i-1].value + K[i-1][w-items[i-1].weight], K[i-1][w]);
            else
                K[i][w] = K[i-1][w];
        }
    }

    int result = K[n][W];
    for (i = 0; i <= n; i++)
        free(K[i]);
    free(K);
    return result;
}




int main() {
    FILE *fp = fopen("instances.csv", "r");
    FILE *out = fopen("average_times.csv", "w");
    FILE *sol = fopen("solutions.csv", "w");
    if (!fp || !out || !sol) {
        printf("Erreur lors de l'ouverture des fichiers.\n");
        return 1;
    }

    // Variables pour stocker les somme des temps et compter les instances par taille de problème
    double sumTimeBT1 = 0, sumTimeBT2 = 0, sumTimeDP = 0;
    int count = 0, currentN = -1;

    char line[4096];
    while (fgets(line, 4096, fp)) {
        int W, n;
        sscanf(line, "%d,%d", &W, &n);

        // Vérifiez si nous passons à une nouvelle taille de problème
        if (n != currentN) {
            if (count > 0) {
                // Écrivez les moyennes pour la taille de problème précédente
                fprintf(out, "%d, %f, %f, %f\n",
                        currentN, sumTimeBT1 / count, sumTimeBT2 / count, sumTimeDP / count);
            }
            // Réinitialisez les compteurs pour la nouvelle taille
            currentN = n;
            sumTimeBT1 = sumTimeBT2 = sumTimeDP = 0;
            count = 0;
        }

        Item items[n];
        char *token = strtok(line, ",");
        token = strtok(NULL, ","); // Passer les deux premiers tokens (W et n)
        token = strtok(NULL, ",");
        for (int i = 0; i < n && token != NULL; i++) {
            sscanf(token, "%d", &items[i].weight);
            token = strtok(NULL, ",");
            sscanf(token, "%d", &items[i].value);
            token = strtok(NULL, ",");
        }

        // Ici, insérez la logique pour configurer et appeler vos fonctions de sac à dos.
        printf("n=%d, W=%d\n", n, W);

        g_itmes = items;
        g_n = n;
        g_W = W;
        g_bestValue = 0;       // meilleure valeur trouvée jusqu'à présent
        g_currentValue = 0;    // valeur courante du sac
        g_currentWeight = 0;

        clock_t start = clock();
        knapsackBT1(0);
        int maxValBT1 = g_bestValue;
        clock_t end = clock();
        double timeBT1 = (double)(end - start) / CLOCKS_PER_SEC;
        sumTimeBT1 += timeBT1;

        start = clock();
        int maxValBT2 = knapsackBT2(items, n, W);
        end = clock();
        double timeBT2 = (double)(end - start) / CLOCKS_PER_SEC;
        sumTimeBT2 += timeBT2;

        start = clock();
        int maxValDP = knapsackDP(W, items, n);
        end = clock();
        double timeDP = (double)(end - start) / CLOCKS_PER_SEC;
        sumTimeDP += timeDP;

        count++;

        fprintf(sol, "%d, %d, %f, %d, %f, %d, %f, %d\n",
            n, W, timeBT1, maxValBT1, timeBT2, maxValBT2, timeDP, maxValDP);
    }

    // N'oubliez pas d'écrire les moyennes pour la dernière taille de problème
    if (count > 0) {
        fprintf(out, "%d, %f, %f, %f\n",
                currentN, sumTimeBT1 / count, sumTimeBT2 / count, sumTimeDP / count);
    }

    fclose(fp);
    fclose(out);
    return 0;
}





