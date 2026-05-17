import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import Akima1DInterpolator

def generateCurve(points):
    t = np.array(range(len(points)))
    x = [p["x"] for p in points]
    y = [p["y"] for p in points]

    ti = np.linspace(0, len(points)-1, 250)
    xi = np.interp(ti, t, x)
    yi = np.interp(ti, t, y)

    #plot_points(xi, yi)

    pi = [{"x": xi[i], "y": yi[i]} for i in range(250)]
    return pi

def plot_points(xi, yi):
    with open("coords.json", "r") as f:
        coords = json.load(f)

    for word, coord in coords.items():
        plt.text(coord["x"], -coord["y"], word)
        plt.scatter(coord["x"], -coord["y"], c="b")
    plt.scatter(xi, -yi, c="r")
    plt.show()

with open("word_paths_raw.json") as f:
    word_paths = json.load(f)

curves = {}
for item in word_paths:
    word, path = list(item.items())[0]
    print(word)
    curve = generateCurve(path)
    curves[word] = curve

with open("word_curves.json", "w") as f:
    json.dump(curves, f)