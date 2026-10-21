import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt


def f(wspolczynniki: list, x):
    wynik = 0
    for n, a in enumerate(wspolczynniki):
        wynik += a * x**n
    return wynik

def get_chosen(k) -> int:
    """rozwiązuje nierówność k <= p(p-1)/2 szukając p
    (największej liczby do której można sumować liczby naturalne żeby suma była mniejsza niż p)
    """

    return np.floor(1 + np.sqrt(1 + 8*k)/2) - 1


def krzyzuj(a: int, b: int, szansa_krzyzowania: float, bits: int, maxs: int, mins: int, szansa_mutacji: float):
    bits = int(bits)

    val_a = int(np.round((a - mins) * (2 ** bits - 1) / (maxs - mins)))
    val_b = int(np.round((b - mins) * (2 ** bits - 1) / (maxs - mins)))

    a_bin = f"{val_a:0{bits}b}"
    b_bin = f"{val_b:0{bits}b}"

    czy_krzyzujemy = np.random.random()
    if czy_krzyzujemy < szansa_krzyzowania:
        granica = np.random.randint(0, bits)
        dziecko1 = list(a_bin[:granica] + b_bin[granica:])
        dziecko2 = list(b_bin[:granica] + a_bin[granica:])
    else:
        dziecko1 = list(a_bin)
        dziecko2 = list(b_bin)

    for i in range(len(dziecko1)):
        if np.random.random() < szansa_mutacji:
            dziecko1[i] = '1' if dziecko1[i] == '0' else '0'

    for i in range(len(dziecko2)):
        if np.random.random() < szansa_mutacji:
            dziecko2[i] = '1' if dziecko2[i] == '0' else '0'

    val_d1 = int("".join(dziecko1), 2)
    val_d2 = int("".join(dziecko2), 2)

    f1 = mins + int(np.round(val_d1 * (maxs - mins) / (2 ** bits - 1)))
    f2 = mins + int(np.round(val_d2 * (maxs - mins) / (2 ** bits - 1)))

    return f1, f2

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--populacja', default=100, type=int)
    parser.add_argument('--x-min', default=-1, type=int, help='Granica badanego przedziału')
    parser.add_argument('--x-max', default=21, type=int, help='Granica badanego przedziału')
    parser.add_argument('--szansa-mutacji', default=0.05, type=float, help='Prawdopodonieństwo mutacji pojedyńczego genu po krzyżowaniu', metavar='Wartość od 0 do 1')
    parser.add_argument('--szansa-krzyzowania', default=0.85, type=float, help='Prawdopodobieństwo skrzyżowania się dwóch osobników na etapie krzyżowania', metavar='Wartość od 0 do 1')
    parser.add_argument('--wspolczynniki', nargs='+', default=[6, 5, -0.25], type=float, help='Kolejne współczynniki wielomianu (podawane od najniższego stopnia tzn. a0, a1, a2,...)')
    parser.add_argument('--max-iter', default=20, type=int, help='Maksymalna liczba iteracji')

    args = parser.parse_args()
    populacja = args.populacja
    x_min = args.x_min
    x_max = args.x_max
    szansa_mutacji = args.szansa_mutacji
    szansa_krzyzowania = args.szansa_krzyzowania
    wspolczynniki = args.wspolczynniki
    limit_iteracji = args.max_iter


    norm_x_max = x_max - x_min
    bits = np.ceil(np.log2(norm_x_max))

    max_przyst = []
    avg_przyst = []
    min_przyst = []
    najlepszy_wynik = -np.inf
    j = 0
    limit_stagnacji = 10
    licznik_stagnacji = 0
    first_iter = True
    while True:
        j += 1
        if first_iter:
            df = pd.DataFrame({
                'x' : np.random.randint(x_min, x_max+1, populacja)
            })
            first_iter = False
        else:
            df = pd.DataFrame({
                'x': new_population
            })
        df['y'] = f(wspolczynniki, df['x'])

        max_przys = df['y'].max()
        max_przyst.append(max_przys)
        min_przyst.append(df['y'].min())
        avg_przyst.append(df['y'].mean())

        if max_przys > najlepszy_wynik:
            najlepszy_wynik = max_przys
            licznik_stagnacji = 0
        else:
            licznik_stagnacji += 1

        if licznik_stagnacji >= limit_stagnacji or j >= limit_iteracji:
            break

        df = df.sort_values(by='y', ascending=True).reset_index(drop=True)

        omega = (populacja * (populacja-1)) // 2

        random_ks = np.random.randint(0, omega, populacja)
        new_pops_idx = [get_chosen(k) for k in random_ks]

        new_population = df.loc[new_pops_idx]
        randoms = new_population.sample(frac=1).reset_index(drop=True)

        new_population = []
        for i in range(0, len(randoms), 2):
            d1, d2 = krzyzuj(randoms['x'].iloc[i], randoms['x'].iloc[i+1], szansa_krzyzowania, bits, x_max, x_min, szansa_mutacji)
            new_population.extend([d1, d2])

    x_samples = np.linspace(x_min, x_max, (x_max - x_min) * 1000)
    y_samples = [f(wspolczynniki, x) for x in x_samples]

    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    ax1.plot(x_samples, y_samples)
    ax1.set_title('Wykres badanej funkcji')
    ax1.set_xlim(x_min-1, x_max+1)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')

    ax2.plot(max_przyst, label='Max')
    ax2.plot(min_przyst, label='Min')
    ax2.plot(avg_przyst, label='Avg')
    ax2.set_title('Wartości max, min i śr. funkcji przystosowania w kolejnych pokoleniach', wrap=True)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('Pokolenie')
    ax2.set_ylabel('Wartość f. przystosowania')

    plt.show()

if __name__ == '__main__':
    main()
