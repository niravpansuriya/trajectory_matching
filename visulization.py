import matplotlib.pyplot as plt
import mplsoccer

sorted_sequences = [
    [(20, 30), (30, 40), (40, 50)],
    [
        (20.9, 29.0),
        (20.9, 29.0),
        (20.9, 29.0),
        (29.8, 39.1),
        (29.8, 39.1),
        (42.7, 49.7),
        (85.8, 9.4),
        (30.8, 55.9),
    ],
]

fig, axs = plt.subplots(nrows=5, figsize=(10, 20))
for i, sequence in enumerate(sorted_sequences[:5]):
    ax = axs[i]
    pitch = mplsoccer.Pitch(
        pitch_type="statsbomb",
        pitch_color="grass",
        line_color="white",
        linewidth=2,
        stripe=True,
    )
    pitch.draw(ax=ax)
    x, y = zip(*sequence)
    ax.scatter(x, y, color="red", zorder=2)
    ax.set_title(f"Sequence {i+1}")
    for j in range(len(sequence) - 1):
        ax.annotate(
            "",
            xytext=sequence[j],
            xy=sequence[j + 1],
            arrowprops=dict(arrowstyle="->", color="red", lw=2),
            zorder=1,
        )
plt.show()
